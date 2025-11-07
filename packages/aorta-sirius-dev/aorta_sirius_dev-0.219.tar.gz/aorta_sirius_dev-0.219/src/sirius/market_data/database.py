import asyncio
import datetime
from abc import ABC, abstractmethod
from typing import Optional, List, cast, Dict, Set, Any

from async_lru import alru_cache
from beanie import DecimalAnnotation, Link

from sirius import common
from sirius.common import PersistedDataClass
from sirius.exceptions import DataIntegrityException
from sirius.market_data import Stock, StockMarketData, Option, MarketDataException, OptionMarketData


class Cache(ABC):

    @staticmethod
    @abstractmethod
    async def is_update_cache(*args: List[Any]) -> bool:
        ...

    @staticmethod
    @abstractmethod
    async def update_cache(*args: List[Any]) -> Any:
        ...

    @staticmethod
    @abstractmethod
    async def get_from_data_provider(*args: List[Any]) -> Any:
        ...


class CachedStock(PersistedDataClass, Stock, Cache):  # type:ignore[misc]

    @staticmethod
    @alru_cache(maxsize=50, ttl=86_400)  # 24 hour cache
    async def get_from_data_provider(ticker: str) -> Optional["CachedStock"]:
        from sirius.market_data.alpha_vantage import AlphaVantageStock
        alpha_vantage_stock: AlphaVantageStock = cast(AlphaVantageStock, await AlphaVantageStock._find(ticker))
        return CachedStock(
            id=alpha_vantage_stock.ticker,
            name=alpha_vantage_stock.name,
            ticker=alpha_vantage_stock.ticker,
            currency=alpha_vantage_stock.currency
        )

    @staticmethod
    @alru_cache(maxsize=50, ttl=86_400)  # 24 hour cache
    async def _find(ticker: str) -> Optional["Stock"]:
        cached_stock: CachedStock | None = await CachedStock.get(ticker)
        if cached_stock:
            return cached_stock

        if await CachedStock.is_update_cache(ticker):
            return await CachedStock.update_cache(ticker)

        raise DataIntegrityException(f"Cached stock could not be found in cache nor is supposed to be retrieved from the cached. Ticker: {ticker}")  # This is just kept for best practice.

    @staticmethod
    async def is_update_cache(ticker: str) -> bool:  # type: ignore[override]
        return await CachedStock.get(ticker) is None

    @staticmethod
    async def update_cache(ticker: str) -> Stock:  # type: ignore[override]
        stock = await CachedStock.get_from_data_provider(ticker)
        if not stock:
            raise MarketDataException(f"Could not find stock from data provider with ticker: {ticker}")

        return await stock.save()


class CachedStockMarketData(PersistedDataClass, StockMarketData, Cache):  # type:ignore[misc]
    open: DecimalAnnotation
    high: DecimalAnnotation
    low: DecimalAnnotation
    close: DecimalAnnotation
    stock: Link[CachedStock]  # type: ignore[assignment]

    @staticmethod
    @alru_cache(maxsize=50, ttl=43_200)  # 12 hour cache
    async def get_from_data_provider(ticker: str, from_timestamp: datetime.datetime) -> List["CachedStockMarketData"]:
        from sirius.market_data.alpha_vantage import AlphaVantageStockMarketData
        abstract_stock: Stock = await Stock.get(ticker)
        stock: CachedStock = cast(CachedStock, await CachedStock._get_local_object(abstract_stock))
        latest_market_data_list: List[StockMarketData] = await AlphaVantageStockMarketData._get(abstract_stock, from_timestamp, datetime.datetime.now())

        return [CachedStockMarketData(
            id=f"{market_data.stock.ticker} | {int(market_data.timestamp.timestamp())}",
            open=market_data.open,
            high=market_data.high,
            low=market_data.low,
            close=market_data.close,
            timestamp=market_data.timestamp,
            stock=stock)
            for market_data in latest_market_data_list]

    @staticmethod
    @alru_cache(maxsize=50, ttl=43_200)  # 12 hour cache
    async def _get_all(ticker: str, is_update_cache: bool = True) -> List["CachedStockMarketData"]:
        if not common.is_test_environment():
            all_data_list: List[CachedStockMarketData] = await CachedStockMarketData.find(CachedStockMarketData.stock.id == ticker, fetch_links=False).to_list()  # type: ignore[attr-defined]
        else:
            all_data_list = [c for c in await CachedStockMarketData.find_all().to_list() if c.stock.ref.id == ticker]  # TODO: Add get_underlying_stock()

        if is_update_cache and await CachedStockMarketData.is_update_cache(ticker, all_data_list):
            latest_data: CachedStockMarketData | None = max(all_data_list, key=lambda d: d.timestamp) if all_data_list else None
            all_data_list = all_data_list + await CachedStockMarketData.update_cache(ticker, latest_data.timestamp if latest_data else None)

        return all_data_list

    @staticmethod
    async def _get(abstract_stock: Stock, from_timestamp: datetime.datetime, to_timestamp: datetime.datetime) -> List["StockMarketData"]:
        from_timestamp = common.get_next_business_day_adjusted_date(from_timestamp)
        to_timestamp = common.get_previous_business_day_adjusted_date(to_timestamp)
        cached_data_list: List[CachedStockMarketData] = await CachedStockMarketData._get_all(abstract_stock.ticker)

        return [obj for obj in cached_data_list if from_timestamp <= obj.timestamp <= to_timestamp]

    @staticmethod
    async def is_update_cache(ticker: str, all_data_list: List["CachedStockMarketData"] | None = None) -> bool:  # type: ignore[override]
        all_data_list = await CachedStockMarketData.find(CachedStockMarketData.stock.id == ticker, fetch_links=False).to_list() if not all_data_list else all_data_list  # type: ignore[attr-defined]
        latest_data: CachedStockMarketData | None = max(all_data_list, key=lambda d: d.timestamp) if all_data_list else None
        expected_latest_data_date: datetime.datetime = common.get_previous_business_day(datetime.datetime.now())

        return len(all_data_list) == 0 or (expected_latest_data_date - latest_data.timestamp).days > 1

    @staticmethod
    async def update_cache(ticker: str, from_timestamp: datetime.datetime | None = None) -> List["CachedStockMarketData"]:  # type: ignore[override]
        from_timestamp = (datetime.datetime.now().replace(year=datetime.datetime.now().year - 10)) if not from_timestamp else from_timestamp  # 10 years
        current_data: Dict[str, CachedStockMarketData] = {data.id: data for data in await CachedStockMarketData._get_all(ticker, is_update_cache=False)}
        latest_data: Dict[str, CachedStockMarketData] = {data.id: data for data in await CachedStockMarketData.get_from_data_provider(ticker, from_timestamp)}
        new_data_ids: Set[str] = latest_data.keys() - current_data.keys()
        unique_data_to_update_list: List[CachedStockMarketData] = [latest_data[k] for k in new_data_ids]
        await CachedStockMarketData.insert_many(unique_data_to_update_list)

        return unique_data_to_update_list


class CachedOption(PersistedDataClass, Option, Cache):
    strike_price: DecimalAnnotation
    underlying_stock: Link[CachedStock]  # type: ignore[assignment]

    async def get_underlying_stock(self) -> Stock:
        if isinstance(self.underlying_stock, Link):
            self.underlying_stock = await self.underlying_stock.fetch()

        return self.underlying_stock  # type: ignore[return-value]

    @staticmethod
    async def _find(option_id: str) -> Optional["Option"]:
        return await CachedOption.get(option_id)

    @staticmethod
    @alru_cache(maxsize=50, ttl=86_400)  # 24 hour cache
    async def get_from_data_provider(ticker: str) -> List["CachedOption"]:
        from sirius.market_data.alpha_vantage import AlphaVantageOption
        stock: Stock | None = await Stock.find(ticker)
        if not stock:
            return []

        cached_stock: CachedStock | None = await CachedStock.get(ticker)
        all_option_list: List[AlphaVantageOption] = await AlphaVantageOption._find_all_from_ticker(ticker)
        return [CachedOption(
            id=Option._get_id(ticker, option.expiry_date, option.strike_price, option.type),
            name=Option._get_id(ticker, option.expiry_date, option.strike_price, option.type),
            strike_price=option.strike_price,
            expiry_date=option.expiry_date,
            type=option.type,
            currency=option.currency,
            underlying_stock=cached_stock
        ) for option in all_option_list]

    @staticmethod
    @alru_cache(maxsize=50, ttl=86_400)  # 24 hour cache
    async def _find_all_options(ticker: str, number_of_days_to_expiry: int, is_update_cache: bool = True) -> List["Option"]:
        expiry_date: datetime.date = datetime.datetime.now().date() + datetime.timedelta(days=number_of_days_to_expiry)
        if not common.is_test_environment():
            all_options_list: List[CachedOption] = await CachedOption.find(CachedOption.underlying_stock.id == ticker).to_list()  # type: ignore[attr-defined]
        else:
            all_options_list = [c for c in await CachedOption.find_all().to_list() if c.underlying_stock.ref.id == ticker]

        if is_update_cache and await CachedOption.is_update_cache(ticker, all_options_list):
            all_options_list = await CachedOption.update_cache(ticker)

        return [option for option in all_options_list if option.expiry_date == expiry_date]

    @staticmethod
    async def is_update_cache(ticker: str, all_options_list: List["CachedOption"] | None = None) -> bool:  # type: ignore[override]
        all_options_list = await CachedOption.find(CachedOption.underlying_stock.id == ticker).to_list() if not all_options_list else all_options_list  # type: ignore[attr-defined]
        earliest_option: CachedOption = min(all_options_list, key=lambda o: o.expiry_date) if len(all_options_list) > 0 else None

        return len(all_options_list) == 0 or earliest_option.expiry_date < datetime.datetime.now().date()

    @staticmethod
    async def update_cache(ticker: str) -> List["CachedOption"]:  # type: ignore[override]
        new_data_list: List[CachedOption] = await CachedOption.get_from_data_provider(ticker)
        await CachedOption.find(CachedOption.underlying_stock.id == ticker).delete()  # type: ignore[attr-defined]
        await CachedOption.insert_many(new_data_list)
        return new_data_list


class CachedOptionMarketData(PersistedDataClass, OptionMarketData, Cache):
    id: str  # type: ignore[assignment]
    last: DecimalAnnotation
    last_updated: datetime.datetime
    option: Link[CachedOption]  # type: ignore[assignment]

    async def get_option(self) -> Option:
        if isinstance(self.option, Link):
            self.option = await self.option.fetch()

        return self.option  # type: ignore[return-value]

    @staticmethod
    async def _get_latest(abstract_option: Option, is_update_cache: bool = True) -> "CachedOptionMarketData":
        cached_option_market_data: CachedOptionMarketData | None = await CachedOptionMarketData.get(abstract_option.id)

        if is_update_cache and await CachedOptionMarketData.is_update_cache(abstract_option.id, cached_option_market_data):
            cached_option_market_data = await CachedOptionMarketData.update_cache(abstract_option)

        return cached_option_market_data

    @staticmethod
    async def is_update_cache(option_id: str, cached_option_market_data: Optional["CachedOptionMarketData"] = None) -> bool:  # type: ignore[override]
        cached_option_market_data = await CachedOptionMarketData.get(option_id) if not cached_option_market_data else cached_option_market_data
        allowed_oldest_timestamp: datetime.datetime = common.get_previous_business_day(datetime.datetime.now())
        return not cached_option_market_data or cached_option_market_data.last_updated < allowed_oldest_timestamp

    @staticmethod
    async def get_from_data_provider(abstract_option: Option) -> "CachedOptionMarketData":  # type: ignore[override]
        from sirius.market_data.alpha_vantage import AlphaVantageOptionMarketData
        alpha_vantage_option: AlphaVantageOptionMarketData = await AlphaVantageOptionMarketData._get_latest(abstract_option)
        return CachedOptionMarketData(
            id=alpha_vantage_option.option.id,
            last=alpha_vantage_option.last,
            last_updated=datetime.datetime.now(),
            option=abstract_option  # type: ignore[arg-type]
        )

    @staticmethod
    async def update_cache(abstract_option: Option) -> "CachedOptionMarketData":  # type: ignore[override]
        if not common.is_test_environment():
            all_cached_option_list: List[CachedOption] = await CachedOption.find(CachedOption.underlying_stock.id == abstract_option.underlying_stock.ticker).to_list()  # type: ignore[attr-defined]
        else:
            all_cached_option_list = [c for c in await CachedOption.find_all().to_list() if c.underlying_stock.ref.id == abstract_option.underlying_stock.ticker]

        cached_option_market_data: List[CachedOptionMarketData] = await asyncio.gather(*[CachedOptionMarketData.get_from_data_provider(option) for option in all_cached_option_list])
        cached_option_market_data = await asyncio.gather(*[cached_market_data.save() for cached_market_data in cached_option_market_data])

        return next(o for o in cached_option_market_data if o.id == abstract_option.id)
