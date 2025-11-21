"""
Tests for validators module
"""

import pytest
from crypto_mcp_server.validators import (
    TickerRequest,
    OHLCVRequest,
    OrderBookRequest,
    TradesRequest,
    MarketListRequest,
    validate_exchange,
    validate_timestamp,
)
from crypto_mcp_server.exceptions import ValidationError
from datetime import datetime


class TestTickerRequest:
    """Tests for TickerRequest validator"""

    def test_valid_ticker_request(self):
        """Test valid ticker request"""
        request = TickerRequest(symbol="BTC/USDT", exchange="binance")
        assert request.symbol == "BTC/USDT"
        assert request.exchange == "binance"

    def test_symbol_uppercase_conversion(self):
        """Test symbol is converted to uppercase"""
        request = TickerRequest(symbol="btc/usdt")
        assert request.symbol == "BTC/USDT"

    def test_invalid_symbol_format(self):
        """Test invalid symbol format raises error"""
        with pytest.raises(ValidationError) as exc_info:
            TickerRequest(symbol="BTCUSDT")
        assert "Invalid symbol format" in str(exc_info.value)

    def test_empty_symbol(self):
        """Test empty symbol raises error"""
        with pytest.raises(ValidationError):
            TickerRequest(symbol="")


class TestOHLCVRequest:
    """Tests for OHLCVRequest validator"""

    def test_valid_ohlcv_request(self):
        """Test valid OHLCV request"""
        request = OHLCVRequest(
            symbol="ETH/USDT", timeframe="1h", limit=100, exchange="binance"
        )
        assert request.symbol == "ETH/USDT"
        assert request.timeframe == "1h"
        assert request.limit == 100

    def test_default_values(self):
        """Test default values are applied"""
        request = OHLCVRequest(symbol="BTC/USDT")
        assert request.timeframe == "1h"
        assert request.limit == 100
        assert request.since is None

    def test_invalid_timeframe(self):
        """Test invalid timeframe raises error"""
        with pytest.raises(ValidationError) as exc_info:
            OHLCVRequest(symbol="BTC/USDT", timeframe="3h")
        assert "Invalid timeframe" in str(exc_info.value)

    def test_limit_validation(self):
        """Test limit bounds validation"""
        # Valid limit
        request = OHLCVRequest(symbol="BTC/USDT", limit=500)
        assert request.limit == 500

        # Too large
        with pytest.raises(ValueError):
            OHLCVRequest(symbol="BTC/USDT", limit=2000)

        # Too small
        with pytest.raises(ValueError):
            OHLCVRequest(symbol="BTC/USDT", limit=0)


class TestOrderBookRequest:
    """Tests for OrderBookRequest validator"""

    def test_valid_order_book_request(self):
        """Test valid order book request"""
        request = OrderBookRequest(symbol="BTC/USDT", limit=50)
        assert request.symbol == "BTC/USDT"
        assert request.limit == 50

    def test_default_limit(self):
        """Test default limit value"""
        request = OrderBookRequest(symbol="BTC/USDT")
        assert request.limit == 20


class TestTradesRequest:
    """Tests for TradesRequest validator"""

    def test_valid_trades_request(self):
        """Test valid trades request"""
        request = TradesRequest(symbol="BTC/USDT", limit=100, since=1700000000000)
        assert request.symbol == "BTC/USDT"
        assert request.limit == 100
        assert request.since == 1700000000000

    def test_default_values(self):
        """Test default values"""
        request = TradesRequest(symbol="BTC/USDT")
        assert request.limit == 50
        assert request.since is None


class TestMarketListRequest:
    """Tests for MarketListRequest validator"""

    def test_valid_market_list_request(self):
        """Test valid market list request"""
        request = MarketListRequest(exchange="binance", quote_currency="USDT")
        assert request.exchange == "binance"
        assert request.quote_currency == "USDT"

    def test_optional_fields(self):
        """Test optional fields"""
        request = MarketListRequest()
        assert request.exchange is None
        assert request.quote_currency is None


class TestValidateExchange:
    """Tests for validate_exchange function"""

    def test_valid_exchange(self):
        """Test valid exchange name"""
        supported = ["binance", "coinbase", "kraken"]
        result = validate_exchange("binance", supported)
        assert result == "binance"

    def test_case_insensitive(self):
        """Test exchange validation is case insensitive"""
        supported = ["binance", "coinbase"]
        result = validate_exchange("BINANCE", supported)
        assert result == "binance"

    def test_invalid_exchange(self):
        """Test invalid exchange raises error"""
        supported = ["binance", "coinbase"]
        with pytest.raises(ValidationError) as exc_info:
            validate_exchange("invalid_exchange", supported)
        assert "not supported" in str(exc_info.value)


class TestValidateTimestamp:
    """Tests for validate_timestamp function"""

    def test_valid_timestamp(self):
        """Test valid timestamp conversion"""
        timestamp = 1700000000000  # Nov 14, 2023
        result = validate_timestamp(timestamp)
        assert isinstance(result, datetime)

    def test_none_timestamp(self):
        """Test None timestamp returns None"""
        result = validate_timestamp(None)
        assert result is None

    def test_invalid_timestamp(self):
        """Test invalid timestamp raises error"""
        with pytest.raises(ValidationError):
            validate_timestamp(-1)
