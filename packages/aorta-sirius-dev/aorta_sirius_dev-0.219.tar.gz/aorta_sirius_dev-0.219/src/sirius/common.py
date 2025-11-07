import datetime
import os
from _decimal import Decimal
from abc import ABC
from enum import Enum
from pathlib import Path
from typing import Any, Dict

from async_lru import alru_cache
from beanie import Document
from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict
from starlette import status

from sirius.constants import EnvironmentVariableKey, SiriusEnvironmentSecretKey
from sirius.exceptions import ApplicationException, SDKClientException


class Environment(Enum):
    Production = "Production"
    Test = "Test"
    Development = "Development"


class Currency(Enum):
    AED = "AED"
    AUD = "AUD"
    BDT = "BDT"
    BGN = "BGN"
    CAD = "CAD"
    CHF = "CHF"
    CLP = "CLP"
    CNY = "CNY"
    CRC = "CRC"
    CZK = "CZK"
    DKK = "DKK"
    EGP = "EGP"
    EUR = "EUR"
    GBP = "GBP"
    GEL = "GEL"
    HKD = "HKD"
    HUF = "HUF"
    IDR = "IDR"
    ILS = "ILS"
    INR = "INR"
    JPY = "JPY"
    KES = "KES"
    KRW = "KRW"
    LKR = "LKR"
    MAD = "MAD"
    MXN = "MXN"
    MYR = "MYR"
    NGN = "NGN"
    NOK = "NOK"
    NPR = "NPR"
    NZD = "NZD"
    PHP = "PHP"
    PKR = "PKR"
    PLN = "PLN"
    RON = "RON"
    SEK = "SEK"
    SGD = "SGD"
    THB = "THB"
    TRY = "TRY"
    TZS = "TZS"
    UAH = "UAH"
    UGX = "UGX"
    USD = "USD"
    UYU = "UYU"
    VND = "VND"
    XOF = "XOF"
    ZAR = "ZAR"


class DataClass(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class ImmutableDataClass(DataClass):
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)


class PersistedDataClass(Document, ABC):
    id: str  # type:ignore[assignment]


class EnvironmentSecret(PersistedDataClass):
    value: str


@alru_cache(maxsize=50, ttl=86_400)  # 24 hour cache
async def get_environmental_secret(key: Enum, default_value: str | None = None) -> str:
    if not isinstance(key, Enum):
        raise SDKClientException("The key has to be an Enum")

    environmental_secret: EnvironmentSecret | None = await EnvironmentSecret.get(key.value)

    if not environmental_secret:
        if default_value:
            environmental_secret = await EnvironmentSecret(id=key.value, value=default_value).save()
        elif not is_test_environment():
            raise ApplicationException(f"The environment secret with the following key is not set: {key.value}")
        else:
            return "PLACEHOLDER"

    return environmental_secret.value


def get_environment_variable(key: EnvironmentVariableKey, default_value: str | None = None) -> str:
    value: str | None = os.getenv(key.value)
    if not value and not default_value:
        raise ApplicationException(f"The environment variable with the following key is not set: {key.value}")

    return value if value else default_value


def get_environment() -> Environment:
    try:
        return Environment(get_environment_variable(EnvironmentVariableKey.ENVIRONMENT, "Test"))
    except (ApplicationException, ValueError):  # ValueError is needed because GitHub CI/CD Pipeline has its own Environment Variable
        return Environment.Test


def is_production_environment() -> bool:
    return Environment.Production == get_environment()


def is_test_environment() -> bool:
    return Environment.Test == get_environment()


def is_development_environment() -> bool:
    return Environment.Development == get_environment()


def get_application_name() -> str:
    try:
        return get_environment_variable(EnvironmentVariableKey.APPLICATION_NAME)
    except ApplicationException:
        return Path.cwd().name.title()


def is_dict_include_another_dict(one_dict: Dict[Any, Any], another_dict: Dict[Any, Any]) -> bool:
    if not all(key in one_dict for key in another_dict):
        return False

    for key, value in one_dict.items():
        if another_dict[key] != value:
            return False

    return True


def get_decimal_str(decimal: Decimal) -> str:
    return "{:,.2f}".format(float(decimal))


def get_date_string(date: datetime.date) -> str:
    return date.strftime("%d/%b/%Y")


async def get_central_finite_curve_authentication_headers() -> Dict[str, str]:
    return {"Authorization": f"Bearer {await get_environmental_secret(SiriusEnvironmentSecretKey.API_KEY)}"} if is_production_environment() else {"Authorization": f"Bearer NULL"}


async def verify_token(token: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))) -> None:
    if not is_production_environment():
        return

    if token.credentials != await get_environmental_secret(SiriusEnvironmentSecretKey.API_KEY):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Bearer"}, )


def get_previous_business_day(timestamp: datetime.datetime) -> datetime.datetime:
    previous_business_day: datetime.datetime = timestamp - datetime.timedelta(days=1)
    previous_business_day = previous_business_day.replace(hour=23, minute=59, second=59, microsecond=0)
    return get_previous_business_day_adjusted_date(previous_business_day)


def get_next_business_day_adjusted_date(timestamp: datetime.datetime) -> datetime.datetime:
    next_day: datetime.datetime = timestamp
    while next_day.weekday() >= 5:
        next_day += datetime.timedelta(days=1)
        next_day = next_day.replace(hour=0, minute=0, second=0, microsecond=0)

    return next_day


def get_previous_business_day_adjusted_date(timestamp: datetime.datetime) -> datetime.datetime:
    prev_day: datetime.datetime = timestamp
    while prev_day.weekday() >= 5:
        prev_day -= datetime.timedelta(days=1)
        prev_day = prev_day.replace(hour=23, minute=59, second=59, microsecond=0)

    return prev_day
