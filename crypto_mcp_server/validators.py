"""
Input validation utilities
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from .exceptions import ValidationError


class TickerRequest(BaseModel):
    """Request model for ticker data"""

    symbol: str = Field(..., description="Trading pair symbol (e.g., BTC/USDT)")
    exchange: Optional[str] = Field(None, description="Exchange name")

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """Validate symbol format"""
        if not v or "/" not in v:
            raise ValidationError(
                f"Invalid symbol format: {v}. Expected format: BASE/QUOTE (e.g., BTC/USDT)"
            )
        return v.upper()


class OHLCVRequest(BaseModel):
    """Request model for OHLCV (candlestick) data"""

    symbol: str = Field(..., description="Trading pair symbol")
    timeframe: str = Field(
        default="1h", description="Timeframe (e.g., 1m, 5m, 15m, 1h, 4h, 1d)"
    )
    limit: int = Field(default=100, ge=1, le=1000, description="Number of candles")
    since: Optional[int] = Field(None, description="Start timestamp in milliseconds")
    exchange: Optional[str] = Field(None, description="Exchange name")

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """Validate symbol format"""
        if not v or "/" not in v:
            raise ValidationError(
                f"Invalid symbol format: {v}. Expected format: BASE/QUOTE"
            )
        return v.upper()

    @field_validator("timeframe")
    @classmethod
    def validate_timeframe(cls, v: str) -> str:
        """Validate timeframe format"""
        valid_timeframes = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d", "1w"]
        if v not in valid_timeframes:
            raise ValidationError(
                f"Invalid timeframe: {v}. Valid options: {', '.join(valid_timeframes)}"
            )
        return v


class OrderBookRequest(BaseModel):
    """Request model for order book data"""

    symbol: str = Field(..., description="Trading pair symbol")
    limit: int = Field(default=20, ge=1, le=100, description="Depth of order book")
    exchange: Optional[str] = Field(None, description="Exchange name")

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """Validate symbol format"""
        if not v or "/" not in v:
            raise ValidationError(f"Invalid symbol format: {v}")
        return v.upper()


class TradesRequest(BaseModel):
    """Request model for recent trades"""

    symbol: str = Field(..., description="Trading pair symbol")
    limit: int = Field(default=50, ge=1, le=500, description="Number of trades")
    since: Optional[int] = Field(None, description="Start timestamp in milliseconds")
    exchange: Optional[str] = Field(None, description="Exchange name")

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """Validate symbol format"""
        if not v or "/" not in v:
            raise ValidationError(f"Invalid symbol format: {v}")
        return v.upper()


class MarketListRequest(BaseModel):
    """Request model for listing markets"""

    exchange: Optional[str] = Field(None, description="Exchange name")
    quote_currency: Optional[str] = Field(None, description="Filter by quote currency (e.g., USDT)")


def validate_exchange(exchange: str, supported_exchanges: List[str]) -> str:
    """
    Validate exchange name against supported exchanges.

    Args:
        exchange: Exchange name to validate
        supported_exchanges: List of supported exchange names

    Returns:
        Validated exchange name

    Raises:
        ValidationError: If exchange is not supported
    """
    exchange_lower = exchange.lower()
    if exchange_lower not in supported_exchanges:
        raise ValidationError(
            f"Exchange '{exchange}' not supported. "
            f"Supported exchanges: {', '.join(supported_exchanges)}"
        )
    return exchange_lower


def validate_timestamp(timestamp: Optional[int]) -> Optional[datetime]:
    """
    Validate and convert timestamp to datetime.

    Args:
        timestamp: Unix timestamp in milliseconds

    Returns:
        DateTime object or None

    Raises:
        ValidationError: If timestamp is invalid
    """
    if timestamp is None:
        return None

    try:
        return datetime.fromtimestamp(timestamp / 1000)
    except (ValueError, OSError) as e:
        raise ValidationError(f"Invalid timestamp: {timestamp}. Error: {e}")
