import asyncio
import datetime
import itertools
from decimal import Decimal
from typing import List, Dict, Any, cast, Set, Callable, Optional

import httpx
from async_lru import alru_cache
from pydantic import ConfigDict

from sirius import common
from sirius.common import Currency
from sirius.constants import SiriusEnvironmentSecretKey
from sirius.exceptions import SiriusException, OperationNotSupportedException
from sirius.http_requests import HTTPResponse, ServerSideException, AsyncHTTPSession
from sirius.market_data import Stock, Option, StockMarketData, Exchange, OptionType

OPTIONS_DATE_FORMAT: str = "%b%y"
_session: AsyncHTTPSession | None = None


async def get_base_url() -> str:
    return await common.get_environmental_secret(SiriusEnvironmentSecretKey.IBKR_SERVICE_BASE_URL, "https://ibkr-service:5000/v1/api/")


async def get_session() -> AsyncHTTPSession:
    global _session
    if not _session:
        base_url: str = await common.get_environmental_secret(SiriusEnvironmentSecretKey.IBKR_SERVICE_BASE_URL, "https://ibkr-service:5000/v1/api/")
        _session = AsyncHTTPSession(base_url)
        _session.client = httpx.AsyncClient(verify=False, timeout=60)

    return _session


class IBKRException(SiriusException):
    pass


class IBKRStock(Stock):
    contract_id: int
    model_config = ConfigDict(frozen=True)

    @staticmethod
    @alru_cache(maxsize=50, ttl=86_400)  # 24 hour cache
    async def _find(ticker: str) -> Optional[Stock]:
        base_url: str = await get_base_url()
        session: AsyncHTTPSession = await get_session()
        response: HTTPResponse = await session.get(f"{base_url}iserver/secdef/search?symbol={ticker}&secType=STK")
        filtered_list: List[Dict[str, Any]] = list(filter(lambda d: d["description"] in Exchange, response.data))
        contract_id_list: List[int] = [int(data["conid"]) for data in filtered_list]

        if not contract_id_list:
            return None

        if len(contract_id_list) > 1:
            raise IBKRException(f"More than one stock found for the ticker: {ticker}")

        contract_id: int = contract_id_list[0]
        response = await session.get(f"{base_url}iserver/contract/{contract_id}/info")
        return IBKRStock(
            name=response.data["company_name"],
            currency=Currency(response.data["currency"]),
            ticker=response.data["symbol"],
            contract_id=contract_id
        )


class IBKROption(Option):
    contract_id: int

    @staticmethod
    async def _find(option_id: str) -> Optional["Option"]:
        raise OperationNotSupportedException("Finding IBKR Options using the ID is not yet supported")

    @staticmethod
    async def __get_all_expiry_month_list(stock: IBKRStock, number_of_days_to_expiry: int) -> List[datetime.date]:
        base_url: str = await get_base_url()
        session: AsyncHTTPSession = await get_session()
        response: HTTPResponse = await session.get(f"{base_url}iserver/secdef/search?symbol={stock.ticker}&secType=STK")
        data: Dict[str, Any] = next(filter(lambda c: int(c["conid"]) == stock.contract_id, response.data))
        option_data: Dict[str, Any] = next(filter(lambda o: o["secType"] == "OPT", data["sections"]))
        all_expiry_month_str_list: List[str] = option_data["months"].split(";")
        all_expiry_month_list: List[datetime.date] = [datetime.datetime.strptime(expiry_month, OPTIONS_DATE_FORMAT).date() for expiry_month in all_expiry_month_str_list]

        return [date for date in all_expiry_month_list if (date - datetime.datetime.now().date()).days <= number_of_days_to_expiry]

    @staticmethod
    async def __get_for_strike_and_expiry(stock: IBKRStock, expiry_month: datetime.date, strike_price: Decimal) -> List["IBKROption"]:
        option_list: List[IBKROption] = []
        base_url: str = await get_base_url()
        session: AsyncHTTPSession = await get_session()
        expiry_month_str: str = expiry_month.strftime(OPTIONS_DATE_FORMAT).upper()
        response: HTTPResponse = await session.get(
            f"{base_url}iserver/secdef/info",
            query_params={
                "conid": stock.contract_id,
                "sectype": "OPT",
                "month": expiry_month_str,
                "strike": float(strike_price)}
        )

        for data in response.data:
            expiry_date: datetime.date = datetime.datetime.strptime(data["maturityDate"], '%Y%m%d').date()
            option_type: OptionType = OptionType.CALL if data["right"] == "C" else OptionType.PUT
            option_id: str = Option._get_id(stock.ticker, expiry_date, strike_price, option_type)

            option_list.append(IBKROption(
                id=option_id,
                contract_id=data["conid"],
                strike_price=strike_price,
                expiry_date=expiry_date,
                type=option_type,
                underlying_stock=stock,
                name=option_id,
                currency=stock.currency
            ))

        return option_list

    @staticmethod
    @alru_cache(maxsize=50, ttl=43_200)  # 12 hour cache
    async def _find_all_options(ticker: str, number_of_days_to_expiry: int) -> List[Option]:
        base_url: str = await get_base_url()
        session: AsyncHTTPSession = await get_session()
        abstract_stock: Stock = await Stock.get(ticker)
        stock: IBKRStock = cast(IBKRStock, await IBKRStock._get_local_object(abstract_stock))
        option_contract_list: List[Option] = []
        expiry_month_list: List[datetime.date] = await IBKROption.__get_all_expiry_month_list(stock, number_of_days_to_expiry)
        expiry_month_str_list: List[str] = [expiry_month.strftime(OPTIONS_DATE_FORMAT).upper() for expiry_month in expiry_month_list]

        responses: List[HTTPResponse] = await asyncio.gather(*[
            session.get(f"{base_url}iserver/secdef/strikes", query_params={"conid": stock.contract_id, "sectype": "OPT", "month": expiry_month_str})
            for expiry_month_str in expiry_month_str_list
        ])
        for expiry_month, response in zip(expiry_month_list, responses):
            all_strike_price_set: Set[Decimal] = set([Decimal(str(strike_price)) for strike_price in response.data.get("call", [])])
            all_strike_price_set.update([Decimal(str(strike_price)) for strike_price in response.data.get("put", [])])
            all_option_contract_list: List[IBKROption] = list(itertools.chain.from_iterable(await asyncio.gather(*[
                IBKROption.__get_for_strike_and_expiry(stock, expiry_month, strike_price)
                for strike_price in all_strike_price_set
            ])))

            option_contract_list.extend(
                [option
                 for option in all_option_contract_list
                 if (option.expiry_date - datetime.datetime.now().date()).days == number_of_days_to_expiry]
            )

        return option_contract_list


class IBKRStockMarketData(StockMarketData):

    @staticmethod
    @alru_cache(maxsize=50, ttl=43_200)  # 12 hour cache
    async def _get_raw_ohlc_data(contract_id: int, from_timestamp: datetime.datetime, to_timestamp: datetime.datetime) -> List[Dict[str, Any]]:
        base_url: str = await get_base_url()
        session: AsyncHTTPSession = await get_session()
        DATE_FORMAT: str = "%Y%m%d-%H:%M:%S"
        try:
            response = await session.get(
                f"{base_url}iserver/marketdata/history",
                query_params={
                    "conid": contract_id,
                    "period": "999d",
                    "bar": "1d",
                    "startTime": (to_timestamp + datetime.timedelta(days=1)).strftime(DATE_FORMAT),  # IBKR sends data 1 day earlier, no idea why.
                    "direction": "-1"
                }
            )
        except ServerSideException as e:
            raise ServerSideException("Did not retrieve any historical market data due to: " + str(e))

        data = response.data.get("data", [])
        earliest_data_timestamp = min([datetime.datetime.fromtimestamp(d["t"] / 1000) for d in data])

        if earliest_data_timestamp > from_timestamp:
            more_data = await IBKRStockMarketData._get_raw_ohlc_data(contract_id, from_timestamp, earliest_data_timestamp)
            return list(itertools.chain(data, more_data))

        return data

    @staticmethod
    @alru_cache(maxsize=50, ttl=43_200)  # 60 second cache
    async def _get_raw_latest_ohlc_data(contract_id: int) -> Dict[str, Any]:
        base_url: str = await get_base_url()
        session: AsyncHTTPSession = await get_session()
        is_response_valid: Callable = lambda r: "31" in r.data[0].keys() and r.data[0]["31"] != ""
        number_of_tries: int = 1
        response: HTTPResponse = await session.get(f"{base_url}iserver/marketdata/snapshot", query_params={"conids": contract_id, "fields": "7295,70,71,31,87"})
        while number_of_tries < 5 and not is_response_valid(response):
            await asyncio.sleep(0.1)
            response = await session.get(f"{base_url}iserver/marketdata/snapshot", query_params={"conids": contract_id, "fields": "7295,70,71,31,87"})
            number_of_tries = number_of_tries + 1

        if not is_response_valid(response):
            raise ServerSideException("Did not retrieve any market data.")

        return response.data[0]

    @staticmethod
    async def _get(abstract_stock: Stock, from_timestamp: datetime.datetime, to_timestamp: datetime.datetime) -> List["StockMarketData"]:
        from_timestamp = common.get_next_business_day_adjusted_date(from_timestamp)
        to_timestamp = common.get_previous_business_day_adjusted_date(to_timestamp)
        stock = cast(IBKRStock, await IBKRStock._get_local_object(abstract_stock))
        raw_ohlc_data_list: List[Dict[str, float]] = await IBKRStockMarketData._get_raw_ohlc_data(stock.contract_id, from_timestamp, to_timestamp)

        return [IBKRStockMarketData(
            open=Decimal(str(ohlc_data["o"])),
            high=Decimal(str(ohlc_data["h"])),
            low=Decimal(str(ohlc_data["l"])),
            close=Decimal(str(ohlc_data["c"])),
            timestamp=datetime.datetime.fromtimestamp(ohlc_data["t"] / 1000),
            stock=stock)
            for ohlc_data in raw_ohlc_data_list
            if from_timestamp.timestamp() <= ohlc_data["t"] / 1000 <= to_timestamp.timestamp()]

    @staticmethod
    async def get_latest(abstract_stock: Stock) -> "IBKRStockMarketData":
        ibkr_stock: IBKRStock = cast(IBKRStock, await IBKRStock._get_local_object(abstract_stock))
        raw_data: Dict[str, Any] = await IBKRStockMarketData._get_raw_latest_ohlc_data(ibkr_stock.contract_id)
        open: Decimal = Decimal(raw_data["7295"].replace("H", "").replace("C", ""))
        high: Decimal = Decimal(raw_data["70"].replace("H", "").replace("C", ""))
        low: Decimal = Decimal(raw_data["71"].replace("H", "").replace("C", ""))
        close: Decimal = Decimal(raw_data["31"].replace("H", "").replace("C", ""))
        return IBKRStockMarketData(
            open=open,
            high=high,
            low=low,
            close=close,
            timestamp=datetime.datetime.now(),
            stock=ibkr_stock
        )
