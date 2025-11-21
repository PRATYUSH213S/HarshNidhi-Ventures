"""
Configuration management for the Crypto MCP Server
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Server configuration from environment variables"""

    # API Keys
    BINANCE_API_KEY: Optional[str] = os.getenv("BINANCE_API_KEY")
    BINANCE_API_SECRET: Optional[str] = os.getenv("BINANCE_API_SECRET")
    COINBASE_API_KEY: Optional[str] = os.getenv("COINBASE_API_KEY")
    COINBASE_API_SECRET: Optional[str] = os.getenv("COINBASE_API_SECRET")

    # Server Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "60"))
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))

    # Default Exchange
    DEFAULT_EXCHANGE: str = os.getenv("DEFAULT_EXCHANGE", "binance")

    # Supported exchanges
    SUPPORTED_EXCHANGES = [
        "binance",
        "coinbase",
        "kraken",
        "bitfinex",
        "bitstamp",
        "gemini",
        "kucoin",
        "okx",
        "bybit",
        "gate",
    ]

    # Cache settings
    MAX_CACHE_SIZE: int = 1000
    CACHE_CLEANUP_INTERVAL: int = 300  # 5 minutes

    @classmethod
    def get_exchange_credentials(cls, exchange: str) -> dict:
        """Get API credentials for a specific exchange"""
        exchange = exchange.lower()
        if exchange == "binance":
            return {
                "apiKey": cls.BINANCE_API_KEY,
                "secret": cls.BINANCE_API_SECRET,
            }
        elif exchange == "coinbase":
            return {
                "apiKey": cls.COINBASE_API_KEY,
                "secret": cls.COINBASE_API_SECRET,
            }
        return {}


config = Config()
