from enum import Enum


class EnvironmentVariableKey(Enum):
    ENVIRONMENT = "ENVIRONMENT"
    APPLICATION_NAME = "APPLICATION_NAME"
    DATABASE_CONNECTION_STRING = "DATABASE_CONNECTION_STRING"


class EnvironmentSecretKey:
    pass


class SiriusEnvironmentSecretKey(EnvironmentSecretKey, Enum):
    API_KEY = "API_KEY"
    DISCORD_BOT_TOKEN = "DISCORD_BOT_TOKEN"
    WISE_API_KEY = "WISE_API_KEY"
    IBKR_SERVICE_BASE_URL = "IBKR_SERVICE_BASE_URL"
    ALPHA_VANTAGE_API_KEY = "ALPHA_VANTAGE_API_KEY"
