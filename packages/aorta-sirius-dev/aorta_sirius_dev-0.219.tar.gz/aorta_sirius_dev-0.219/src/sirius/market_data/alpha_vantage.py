import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional

from async_lru import alru_cache

from sirius import common
from sirius.common import Currency
from sirius.constants import SiriusEnvironmentSecretKey
from sirius.http_requests import AsyncHTTPSession, HTTPResponse
from sirius.market_data import Option, Stock, OptionType, OptionMarketData, StockMarketData

BASE_URL: str = "https://www.alphavantage.co/query"


class AlphaVantageOption(Option):

    @staticmethod
    @alru_cache(maxsize=50, ttl=43_200)  # 12 hour cache
    async def _get_raw_data(ticker: str) -> Dict[Any, Any]:
        api_key: str = await common.get_environmental_secret(SiriusEnvironmentSecretKey.ALPHA_VANTAGE_API_KEY)
        response: HTTPResponse = await AsyncHTTPSession(BASE_URL).get(f"{BASE_URL}", query_params={
            "function": "HISTORICAL_OPTIONS",
            "symbol": ticker,
            "apikey": api_key
        })

        return response.data

    @staticmethod
    async def _find(option_id: str) -> Optional["Option"]:
        ticker: str = option_id.split(" | ")[0]
        option_list: List[AlphaVantageOption] = await AlphaVantageOption._find_all_from_ticker(ticker)
        option_map: Dict[str, AlphaVantageOption] = {option.id: option for option in option_list}
        return option_map.get(option_id)

    @staticmethod
    async def _find_all_from_ticker(ticker: str) -> List["AlphaVantageOption"]:
        option_list: List[AlphaVantageOption] = []
        underlying_stock: Stock = await Stock.find(ticker)
        if not underlying_stock:
            return []

        raw_data: Dict[Any, Any] = await AlphaVantageOption._get_raw_data(ticker)
        for data in raw_data["data"]:
            expiry_date: datetime.date = datetime.datetime.strptime(data["expiration"], "%Y-%m-%d").date()
            if expiry_date < datetime.datetime.now().date():
                continue

            strike_price: Decimal = Decimal(data["strike"])
            option_type: OptionType = OptionType(str(data["type"]).upper())
            option_id: str = Option._get_id(ticker, expiry_date, strike_price, option_type)
            option_list.append(AlphaVantageOption(
                id=option_id,
                underlying_stock=underlying_stock,
                strike_price=strike_price,
                expiry_date=expiry_date,
                type=option_type,
                currency=underlying_stock.currency,
                name=option_id
            ))

        return option_list

    @staticmethod
    async def _find_all_options(ticker: str, number_of_days_to_expiry: int) -> List["Option"]:
        data = await AlphaVantageOption._find_all_from_ticker(ticker)
        return [option for option in data
                if (option.expiry_date - datetime.datetime.now().date()).days == number_of_days_to_expiry]


class AlphaVantageOptionMarketData(OptionMarketData):

    @staticmethod
    @alru_cache(maxsize=50, ttl=43_200)  # 12 hour cache
    async def _get_all_last_map(ticker: str) -> Dict[str, Decimal]:
        all_last_map: Dict[str, Decimal] = {}
        raw_data: Dict[Any, Any] = await AlphaVantageOption._get_raw_data(ticker)
        for data in raw_data["data"]:
            expiry_date: datetime.date = datetime.datetime.strptime(data["expiration"], "%Y-%m-%d").date()
            strike_price: Decimal = Decimal(data["strike"])
            option_type: OptionType = OptionType(str(data["type"]).upper())
            option_id: str = Option._get_id(ticker, expiry_date, strike_price, option_type)
            all_last_map[option_id] = Decimal(data["last"])

        return all_last_map

    @staticmethod
    async def _get_latest(abstract_option: Option) -> "AlphaVantageOptionMarketData":
        underlying_stock: Stock = await abstract_option.get_underlying_stock()
        all_map: Dict[str, Decimal] = await AlphaVantageOptionMarketData._get_all_last_map(underlying_stock.ticker)
        last: Decimal = all_map[abstract_option.id]
        return AlphaVantageOptionMarketData(option=abstract_option, last=last)


class AlphaVantageStockMarketData(StockMarketData):

    @staticmethod
    @alru_cache(maxsize=50, ttl=43_200)  # 12 hour cache
    async def _get_raw_time_series_data(ticker: str) -> Dict[Any, Any]:
        api_key: str = await common.get_environmental_secret(SiriusEnvironmentSecretKey.ALPHA_VANTAGE_API_KEY)
        response: HTTPResponse = await AsyncHTTPSession(BASE_URL).get(f"{BASE_URL}", query_params={
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker,
            "outputsize": "full",
            "apikey": api_key
        })

        return response.data["Time Series (Daily)"]

    @staticmethod
    @alru_cache(maxsize=50, ttl=60)  # 60 second cache
    async def _get_raw_latest_stock_market_data(ticker: str) -> Dict[Any, Any]:
        api_key: str = await common.get_environmental_secret(SiriusEnvironmentSecretKey.ALPHA_VANTAGE_API_KEY)
        response: HTTPResponse = await AsyncHTTPSession(BASE_URL).get(f"{BASE_URL}", query_params={
            "function": "GLOBAL_QUOTE",
            "symbol": ticker,
            "apikey": api_key
        })

        return response.data["Global Quote"]

    @staticmethod
    async def _get(abstract_stock: Stock, from_timestamp: datetime.datetime, to_timestamp: datetime.datetime) -> List["StockMarketData"]:
        raw_data: Dict[Any, Any] = await AlphaVantageStockMarketData._get_raw_time_series_data(abstract_stock.ticker)
        return [AlphaVantageStockMarketData(
            open=Decimal(raw_data[date_string]["1. open"]),
            high=Decimal(raw_data[date_string]["2. high"]),
            low=Decimal(raw_data[date_string]["3. low"]),
            close=Decimal(raw_data[date_string]["4. close"]),
            timestamp=datetime.datetime.strptime(date_string, "%Y-%m-%d"),
            stock=abstract_stock
        ) for date_string in raw_data.keys()
            if from_timestamp.timestamp() <= datetime.datetime.strptime(date_string, "%Y-%m-%d").timestamp() <= to_timestamp.timestamp()]

    @staticmethod
    async def get_latest(abstract_stock: Stock) -> "AlphaVantageStockMarketData":
        raw_data: Dict[Any, Any] = await AlphaVantageStockMarketData._get_raw_latest_stock_market_data(abstract_stock.ticker)

        return AlphaVantageStockMarketData(
            open=Decimal(raw_data["02. open"]),
            high=Decimal(raw_data["03. high"]),
            low=Decimal(raw_data["04. low"]),
            close=Decimal(raw_data["05. price"]),
            timestamp=datetime.datetime.strptime(raw_data["07. latest trading day"], "%Y-%m-%d"),
            stock=abstract_stock
        )


class AlphaVantageStock(Stock):

    @staticmethod
    @alru_cache(maxsize=50, ttl=86_400)  # 24 hour cache
    async def _get_raw_ticker_search_data(ticker: str) -> List[Dict[str, Any]]:
        api_key: str = await common.get_environmental_secret(SiriusEnvironmentSecretKey.ALPHA_VANTAGE_API_KEY)
        response: HTTPResponse = await AsyncHTTPSession(BASE_URL).get(f"{BASE_URL}", query_params={
            "function": "SYMBOL_SEARCH",
            "keywords": ticker,
            "apikey": api_key
        })

        return response.data["bestMatches"]

    @staticmethod
    async def _find(ticker: str) -> Optional["Stock"]:
        raw_data_list: List[Dict[str, Any]] = await AlphaVantageStock._get_raw_ticker_search_data(ticker)
        try:
            raw_data: Dict[str, Any] = max((raw_data for raw_data in raw_data_list if raw_data["1. symbol"] == ticker and raw_data["4. region"] == "United States" and raw_data["8. currency"] == "USD"), key=lambda r: float(r["9. matchScore"]))
        except ValueError:
            return None

        return AlphaVantageStock(
            name=raw_data['2. name'],
            currency=Currency(raw_data['8. currency']),
            ticker=raw_data['1. symbol']
        )
