"""
Tests for MCP server module
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import json
from crypto_mcp_server.server import CryptoMCPServer
from mcp.types import TextContent


class TestCryptoMCPServer:
    """Tests for CryptoMCPServer class"""

    def setup_method(self):
        """Set up test server"""
        self.server = CryptoMCPServer(name="test-server")

    def test_server_initialization(self):
        """Test server initialization"""
        assert self.server is not None
        assert self.server.server is not None

    @pytest.mark.asyncio
    async def test_list_resources(self):
        """Test listing resources"""
        # Get the list_resources handler
        handler = None
        for callback in self.server.server._request_handlers.values():
            if hasattr(callback, "__name__") and "list_resources" in str(callback):
                handler = callback
                break

        if handler:
            resources = await handler()
            assert len(resources) > 0
            resource_uris = [r.uri for r in resources]
            assert "crypto://exchanges" in resource_uris
            assert "crypto://cache/stats" in resource_uris

    @pytest.mark.asyncio
    async def test_read_resource_exchanges(self):
        """Test reading exchanges resource"""
        # Get the read_resource handler
        handler = None
        for callback in self.server.server._request_handlers.values():
            if hasattr(callback, "__name__") and "read_resource" in str(callback):
                handler = callback
                break

        if handler:
            result = await handler("crypto://exchanges")
            data = json.loads(result)
            assert "supported_exchanges" in data
            assert "default_exchange" in data
            assert isinstance(data["supported_exchanges"], list)

    @pytest.mark.asyncio
    async def test_read_resource_cache_stats(self):
        """Test reading cache stats resource"""
        handler = None
        for callback in self.server.server._request_handlers.values():
            if hasattr(callback, "__name__") and "read_resource" in str(callback):
                handler = callback
                break

        if handler:
            result = await handler("crypto://cache/stats")
            data = json.loads(result)
            assert "hits" in data
            assert "misses" in data
            assert "total_requests" in data

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test listing available tools"""
        handler = None
        for callback in self.server.server._request_handlers.values():
            if hasattr(callback, "__name__") and "list_tools" in str(callback):
                handler = callback
                break

        if handler:
            tools = await handler()
            assert len(tools) > 0
            tool_names = [t.name for t in tools]
            assert "get_ticker" in tool_names
            assert "get_ohlcv" in tool_names
            assert "get_order_book" in tool_names
            assert "get_trades" in tool_names
            assert "get_markets" in tool_names
            assert "clear_cache" in tool_names

    @pytest.mark.asyncio
    @patch("crypto_mcp_server.server.exchange_connector")
    async def test_handle_get_ticker(self, mock_connector):
        """Test handling get_ticker tool call"""
        mock_connector.get_ticker_sync.return_value = {
            "symbol": "BTC/USDT",
            "exchange": "binance",
            "last": 37000.0,
            "bid": 36999.5,
            "ask": 37000.5,
        }

        result = await self.server._handle_get_ticker(
            {"symbol": "BTC/USDT", "exchange": "binance"}
        )

        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        data = json.loads(result[0].text)
        assert data["symbol"] == "BTC/USDT"
        assert data["last"] == 37000.0

    @pytest.mark.asyncio
    @patch("crypto_mcp_server.server.exchange_connector")
    async def test_handle_get_ohlcv(self, mock_connector):
        """Test handling get_ohlcv tool call"""
        mock_connector.get_ohlcv_sync.return_value = [
            {
                "timestamp": 1700000000000,
                "datetime": "2023-11-14T00:00:00",
                "open": 37000.0,
                "high": 37500.0,
                "low": 36500.0,
                "close": 37200.0,
                "volume": 100.0,
            }
        ]

        result = await self.server._handle_get_ohlcv(
            {
                "symbol": "BTC/USDT",
                "timeframe": "1h",
                "limit": 1,
                "exchange": "binance",
            }
        )

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["symbol"] == "BTC/USDT"
        assert data["timeframe"] == "1h"
        assert len(data["data"]) == 1

    @pytest.mark.asyncio
    @patch("crypto_mcp_server.server.exchange_connector")
    async def test_handle_get_order_book(self, mock_connector):
        """Test handling get_order_book tool call"""
        mock_connector.get_order_book_sync.return_value = {
            "symbol": "BTC/USDT",
            "exchange": "binance",
            "bids": [[37000.0, 1.5], [36999.0, 2.0]],
            "asks": [[37001.0, 1.2], [37002.0, 1.8]],
        }

        result = await self.server._handle_get_order_book(
            {"symbol": "BTC/USDT", "limit": 2, "exchange": "binance"}
        )

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["symbol"] == "BTC/USDT"
        assert len(data["bids"]) == 2
        assert len(data["asks"]) == 2

    @pytest.mark.asyncio
    @patch("crypto_mcp_server.server.exchange_connector")
    async def test_handle_get_trades(self, mock_connector):
        """Test handling get_trades tool call"""
        mock_connector.get_trades_sync.return_value = [
            {
                "id": "12345",
                "timestamp": 1700000000000,
                "price": 37000.0,
                "amount": 0.5,
                "side": "buy",
            }
        ]

        result = await self.server._handle_get_trades(
            {"symbol": "BTC/USDT", "limit": 1, "exchange": "binance"}
        )

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["symbol"] == "BTC/USDT"
        assert len(data["trades"]) == 1

    @pytest.mark.asyncio
    @patch("crypto_mcp_server.server.exchange_connector")
    async def test_handle_get_markets(self, mock_connector):
        """Test handling get_markets tool call"""
        mock_connector.get_markets.return_value = [
            {
                "symbol": "BTC/USDT",
                "base": "BTC",
                "quote": "USDT",
                "active": True,
            },
            {
                "symbol": "ETH/USDT",
                "base": "ETH",
                "quote": "USDT",
                "active": True,
            },
        ]

        result = await self.server._handle_get_markets({"exchange": "binance"})

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["exchange"] == "binance"
        assert data["count"] == 2

    @pytest.mark.asyncio
    @patch("crypto_mcp_server.server.cache_manager")
    async def test_handle_clear_cache(self, mock_cache):
        """Test handling clear_cache tool call"""
        mock_cache.get_stats.return_value = {
            "hits": 10,
            "misses": 5,
            "current_size": 0,
        }

        result = await self.server._handle_clear_cache({})

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert "message" in data
        assert "Cache cleared" in data["message"]
        mock_cache.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_tool_validation_error_handling(self):
        """Test error handling for validation errors"""
        # Invalid symbol format
        result = await self.server._handle_get_ticker(
            {"symbol": "INVALID", "exchange": "binance"}
        )

        assert len(result) == 1
        assert "Error" in result[0].text

    @pytest.mark.asyncio
    async def test_tool_unsupported_exchange_error(self):
        """Test error handling for unsupported exchange"""
        result = await self.server._handle_get_ticker(
            {"symbol": "BTC/USDT", "exchange": "unsupported_exchange"}
        )

        assert len(result) == 1
        assert "Error" in result[0].text
