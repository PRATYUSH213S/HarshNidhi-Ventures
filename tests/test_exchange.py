"""
Tests for exchange connector module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from crypto_mcp_server.exchange import ExchangeConnector
from crypto_mcp_server.exceptions import (
    ExchangeNotSupportedError,
    ExchangeConnectionError,
    DataFetchError,
    InvalidSymbolError,
)
import ccxt


class TestExchangeConnector:
    """Tests for ExchangeConnector class"""

    def setup_method(self):
        """Set up test exchange connector"""
        self.connector = ExchangeConnector()

    @patch("crypto_mcp_server.exchange.ccxt")
    def test_get_exchange_creates_new_instance(self, mock_ccxt):
        """Test creating new exchange instance"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {}
        mock_ccxt.binance = Mock(return_value=mock_exchange)

        exchange = self.connector._get_exchange("binance")

        assert exchange is not None
        mock_exchange.load_markets.assert_called_once()

    def test_get_exchange_unsupported(self):
        """Test getting unsupported exchange raises error"""
        with pytest.raises(ExchangeNotSupportedError):
            self.connector._get_exchange("unsupported_exchange")

    @patch("crypto_mcp_server.exchange.ccxt")
    def test_get_exchange_reuses_instance(self, mock_ccxt):
        """Test reusing existing exchange instance"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {}
        mock_ccxt.binance = Mock(return_value=mock_exchange)

        exchange1 = self.connector._get_exchange("binance")
        exchange2 = self.connector._get_exchange("binance")

        assert exchange1 is exchange2
        mock_exchange.load_markets.assert_called_once()

    @patch("crypto_mcp_server.exchange.ccxt")
    @patch("crypto_mcp_server.exchange.rate_limiter")
    def test_get_ticker_sync(self, mock_rate_limiter, mock_ccxt):
        """Test getting ticker data synchronously"""
        mock_exchange = Mock()
        mock_exchange.fetch_ticker.return_value = {
            "symbol": "BTC/USDT",
            "timestamp": 1700000000000,
            "datetime": "2023-11-14T00:00:00.000Z",
            "last": 37000.0,
            "bid": 36999.5,
            "ask": 37000.5,
            "high": 37500.0,
            "low": 36500.0,
            "baseVolume": 1234.56,
            "quoteVolume": 45678900.0,
            "change": 500.0,
            "percentage": 1.37,
        }
        mock_exchange.load_markets.return_value = {}
        mock_ccxt.binance = Mock(return_value=mock_exchange)

        ticker = self.connector.get_ticker_sync("BTC/USDT", "binance")

        assert ticker["symbol"] == "BTC/USDT"
        assert ticker["last"] == 37000.0
        assert ticker["exchange"] == "binance"
        mock_rate_limiter.record_request.assert_called_once_with("binance")

    @patch("crypto_mcp_server.exchange.ccxt")
    @patch("crypto_mcp_server.exchange.rate_limiter")
    def test_get_ticker_invalid_symbol(self, mock_rate_limiter, mock_ccxt):
        """Test getting ticker with invalid symbol raises error"""
        mock_exchange = Mock()
        mock_exchange.fetch_ticker.side_effect = ccxt.BadSymbol("Invalid symbol")
        mock_exchange.load_markets.return_value = {}
        mock_ccxt.binance = Mock(return_value=mock_exchange)

        with pytest.raises(InvalidSymbolError):
            self.connector.get_ticker_sync("INVALID", "binance")

    @patch("crypto_mcp_server.exchange.ccxt")
    @patch("crypto_mcp_server.exchange.rate_limiter")
    def test_get_ohlcv_sync(self, mock_rate_limiter, mock_ccxt):
        """Test getting OHLCV data synchronously"""
        mock_exchange = Mock()
        mock_exchange.fetch_ohlcv.return_value = [
            [1700000000000, 37000.0, 37500.0, 36500.0, 37200.0, 100.0],
            [1700003600000, 37200.0, 37800.0, 37100.0, 37600.0, 120.0],
        ]
        mock_exchange.load_markets.return_value = {}
        mock_ccxt.binance = Mock(return_value=mock_exchange)

        ohlcv = self.connector.get_ohlcv_sync("BTC/USDT", "1h", "binance", limit=2)

        assert len(ohlcv) == 2
        assert ohlcv[0]["open"] == 37000.0
        assert ohlcv[0]["close"] == 37200.0
        assert "datetime" in ohlcv[0]

    @patch("crypto_mcp_server.exchange.ccxt")
    @patch("crypto_mcp_server.exchange.rate_limiter")
    def test_get_order_book_sync(self, mock_rate_limiter, mock_ccxt):
        """Test getting order book synchronously"""
        mock_exchange = Mock()
        mock_exchange.fetch_order_book.return_value = {
            "timestamp": 1700000000000,
            "datetime": "2023-11-14T00:00:00.000Z",
            "bids": [[37000.0, 1.5], [36999.0, 2.0]],
            "asks": [[37001.0, 1.2], [37002.0, 1.8]],
        }
        mock_exchange.load_markets.return_value = {}
        mock_ccxt.binance = Mock(return_value=mock_exchange)

        order_book = self.connector.get_order_book_sync("BTC/USDT", "binance", limit=2)

        assert order_book["symbol"] == "BTC/USDT"
        assert len(order_book["bids"]) == 2
        assert len(order_book["asks"]) == 2
        assert order_book["bids"][0][0] == 37000.0

    @patch("crypto_mcp_server.exchange.ccxt")
    @patch("crypto_mcp_server.exchange.rate_limiter")
    def test_get_trades_sync(self, mock_rate_limiter, mock_ccxt):
        """Test getting trades synchronously"""
        mock_exchange = Mock()
        mock_exchange.fetch_trades.return_value = [
            {
                "id": "12345",
                "timestamp": 1700000000000,
                "datetime": "2023-11-14T00:00:00.000Z",
                "symbol": "BTC/USDT",
                "type": "limit",
                "side": "buy",
                "price": 37000.0,
                "amount": 0.5,
                "cost": 18500.0,
            }
        ]
        mock_exchange.load_markets.return_value = {}
        mock_ccxt.binance = Mock(return_value=mock_exchange)

        trades = self.connector.get_trades_sync("BTC/USDT", "binance", limit=1)

        assert len(trades) == 1
        assert trades[0]["id"] == "12345"
        assert trades[0]["price"] == 37000.0
        assert trades[0]["side"] == "buy"

    @patch("crypto_mcp_server.exchange.ccxt")
    def test_get_markets(self, mock_ccxt):
        """Test getting available markets"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            "BTC/USDT": {
                "symbol": "BTC/USDT",
                "base": "BTC",
                "quote": "USDT",
                "active": True,
                "type": "spot",
                "spot": True,
                "margin": False,
                "future": False,
                "swap": False,
            },
            "ETH/USDT": {
                "symbol": "ETH/USDT",
                "base": "ETH",
                "quote": "USDT",
                "active": True,
                "type": "spot",
                "spot": True,
                "margin": False,
                "future": False,
                "swap": False,
            },
        }
        mock_ccxt.binance = Mock(return_value=mock_exchange)

        markets = self.connector.get_markets("binance")

        assert len(markets) == 2
        assert markets[0]["symbol"] in ["BTC/USDT", "ETH/USDT"]
        assert markets[0]["base"] in ["BTC", "ETH"]

    @patch("crypto_mcp_server.exchange.ccxt")
    def test_get_markets_filter_by_quote(self, mock_ccxt):
        """Test filtering markets by quote currency"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            "BTC/USDT": {
                "symbol": "BTC/USDT",
                "base": "BTC",
                "quote": "USDT",
                "active": True,
                "type": "spot",
                "spot": True,
                "margin": False,
                "future": False,
                "swap": False,
            },
            "BTC/BTC": {
                "symbol": "ETH/BTC",
                "base": "ETH",
                "quote": "BTC",
                "active": True,
                "type": "spot",
                "spot": True,
                "margin": False,
                "future": False,
                "swap": False,
            },
        }
        mock_ccxt.binance = Mock(return_value=mock_exchange)

        markets = self.connector.get_markets("binance", quote_currency="USDT")

        assert len(markets) == 1
        assert markets[0]["quote"] == "USDT"

    def test_close_specific_exchange(self):
        """Test closing specific exchange connection"""
        with patch("crypto_mcp_server.exchange.ccxt") as mock_ccxt:
            mock_exchange = Mock()
            mock_exchange.load_markets.return_value = {}
            mock_ccxt.binance = Mock(return_value=mock_exchange)

            self.connector._get_exchange("binance")
            self.connector.close("binance")

            assert "binance" not in self.connector._exchanges

    def test_close_all_exchanges(self):
        """Test closing all exchange connections"""
        with patch("crypto_mcp_server.exchange.ccxt") as mock_ccxt:
            mock_exchange = Mock()
            mock_exchange.load_markets.return_value = {}
            mock_ccxt.binance = Mock(return_value=mock_exchange)
            mock_ccxt.coinbase = Mock(return_value=mock_exchange)

            self.connector._get_exchange("binance")
            self.connector._get_exchange("coinbase")
            self.connector.close()

            assert len(self.connector._exchanges) == 0
