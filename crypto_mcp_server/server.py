"""
Main MCP Server implementation for cryptocurrency market data
"""

import asyncio
import json
from typing import Any, Optional
from mcp.server import Server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
from mcp.server.stdio import stdio_server

from .config import config
from .logger import logger
from .exchange import exchange_connector
from .cache import cache_manager
from .validators import (
    TickerRequest,
    OHLCVRequest,
    OrderBookRequest,
    TradesRequest,
    MarketListRequest,
    validate_exchange,
)
from .exceptions import (
    CryptoMCPError,
    ValidationError,
    ExchangeNotSupportedError,
    DataFetchError,
)


class CryptoMCPServer:
    """MCP Server for cryptocurrency market data"""

    def __init__(self, name: str = "crypto-mcp-server"):
        """
        Initialize the MCP server.

        Args:
            name: Server name
        """
        self.server = Server(name)
        self._setup_handlers()
        logger.info(f"CryptoMCPServer '{name}' initialized")

    def _setup_handlers(self) -> None:
        """Set up MCP protocol handlers"""

        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """List available resources"""
            logger.debug("Listing resources")
            return [
                Resource(
                    uri="crypto://exchanges",
                    name="Supported Exchanges",
                    mimeType="application/json",
                    description="List of supported cryptocurrency exchanges",
                ),
                Resource(
                    uri="crypto://cache/stats",
                    name="Cache Statistics",
                    mimeType="application/json",
                    description="Current cache performance statistics",
                ),
            ]

        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a specific resource"""
            logger.debug(f"Reading resource: {uri}")

            if uri == "crypto://exchanges":
                return json.dumps(
                    {
                        "supported_exchanges": config.SUPPORTED_EXCHANGES,
                        "default_exchange": config.DEFAULT_EXCHANGE,
                    },
                    indent=2,
                )
            elif uri == "crypto://cache/stats":
                return json.dumps(cache_manager.get_stats(), indent=2)
            else:
                raise ValueError(f"Unknown resource: {uri}")

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools"""
            logger.debug("Listing tools")
            return [
                Tool(
                    name="get_ticker",
                    description="Get current price and market data for a cryptocurrency pair",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Trading pair symbol (e.g., BTC/USDT)",
                            },
                            "exchange": {
                                "type": "string",
                                "description": f"Exchange name (default: {config.DEFAULT_EXCHANGE})",
                            },
                        },
                        "required": ["symbol"],
                    },
                ),
                Tool(
                    name="get_ohlcv",
                    description="Get historical OHLCV (candlestick) data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Trading pair symbol",
                            },
                            "timeframe": {
                                "type": "string",
                                "description": "Timeframe (1m, 5m, 15m, 1h, 4h, 1d, etc.)",
                                "default": "1h",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of candles (max 1000)",
                                "default": 100,
                            },
                            "since": {
                                "type": "integer",
                                "description": "Start timestamp in milliseconds",
                            },
                            "exchange": {
                                "type": "string",
                                "description": f"Exchange name (default: {config.DEFAULT_EXCHANGE})",
                            },
                        },
                        "required": ["symbol"],
                    },
                ),
                Tool(
                    name="get_order_book",
                    description="Get current order book (market depth) data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Trading pair symbol",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Depth of order book (max 100)",
                                "default": 20,
                            },
                            "exchange": {
                                "type": "string",
                                "description": f"Exchange name (default: {config.DEFAULT_EXCHANGE})",
                            },
                        },
                        "required": ["symbol"],
                    },
                ),
                Tool(
                    name="get_trades",
                    description="Get recent trades for a trading pair",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Trading pair symbol",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of trades (max 500)",
                                "default": 50,
                            },
                            "since": {
                                "type": "integer",
                                "description": "Start timestamp in milliseconds",
                            },
                            "exchange": {
                                "type": "string",
                                "description": f"Exchange name (default: {config.DEFAULT_EXCHANGE})",
                            },
                        },
                        "required": ["symbol"],
                    },
                ),
                Tool(
                    name="get_markets",
                    description="Get list of available trading pairs on an exchange",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "exchange": {
                                "type": "string",
                                "description": f"Exchange name (default: {config.DEFAULT_EXCHANGE})",
                            },
                            "quote_currency": {
                                "type": "string",
                                "description": "Filter by quote currency (e.g., USDT, BTC)",
                            },
                        },
                    },
                ),
                Tool(
                    name="clear_cache",
                    description="Clear the server cache",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Execute a tool"""
            logger.info(f"Tool called: {name} with arguments: {arguments}")

            try:
                if name == "get_ticker":
                    return await self._handle_get_ticker(arguments)
                elif name == "get_ohlcv":
                    return await self._handle_get_ohlcv(arguments)
                elif name == "get_order_book":
                    return await self._handle_get_order_book(arguments)
                elif name == "get_trades":
                    return await self._handle_get_trades(arguments)
                elif name == "get_markets":
                    return await self._handle_get_markets(arguments)
                elif name == "clear_cache":
                    return await self._handle_clear_cache(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")

            except ValidationError as e:
                logger.error(f"Validation error in {name}: {e}")
                return [TextContent(type="text", text=f"Validation Error: {str(e)}")]
            except ExchangeNotSupportedError as e:
                logger.error(f"Exchange not supported in {name}: {e}")
                return [TextContent(type="text", text=f"Exchange Error: {str(e)}")]
            except DataFetchError as e:
                logger.error(f"Data fetch error in {name}: {e}")
                return [TextContent(type="text", text=f"Data Fetch Error: {str(e)}")]
            except CryptoMCPError as e:
                logger.error(f"MCP error in {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
            except Exception as e:
                logger.exception(f"Unexpected error in {name}: {e}")
                return [
                    TextContent(type="text", text=f"Unexpected Error: {str(e)}")
                ]

    async def _handle_get_ticker(self, arguments: dict) -> list[TextContent]:
        """Handle get_ticker tool call"""
        request = TickerRequest(
            symbol=arguments["symbol"],
            exchange=arguments.get("exchange", config.DEFAULT_EXCHANGE),
        )

        validate_exchange(request.exchange, config.SUPPORTED_EXCHANGES)

        ticker = exchange_connector.get_ticker_sync(request.symbol, request.exchange)

        return [
            TextContent(
                type="text",
                text=json.dumps(ticker, indent=2),
            )
        ]

    async def _handle_get_ohlcv(self, arguments: dict) -> list[TextContent]:
        """Handle get_ohlcv tool call"""
        request = OHLCVRequest(
            symbol=arguments["symbol"],
            timeframe=arguments.get("timeframe", "1h"),
            limit=arguments.get("limit", 100),
            since=arguments.get("since"),
            exchange=arguments.get("exchange", config.DEFAULT_EXCHANGE),
        )

        validate_exchange(request.exchange, config.SUPPORTED_EXCHANGES)

        ohlcv = exchange_connector.get_ohlcv_sync(
            request.symbol,
            request.timeframe,
            request.exchange,
            request.limit,
            request.since,
        )

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "symbol": request.symbol,
                        "exchange": request.exchange,
                        "timeframe": request.timeframe,
                        "count": len(ohlcv),
                        "data": ohlcv,
                    },
                    indent=2,
                ),
            )
        ]

    async def _handle_get_order_book(self, arguments: dict) -> list[TextContent]:
        """Handle get_order_book tool call"""
        request = OrderBookRequest(
            symbol=arguments["symbol"],
            limit=arguments.get("limit", 20),
            exchange=arguments.get("exchange", config.DEFAULT_EXCHANGE),
        )

        validate_exchange(request.exchange, config.SUPPORTED_EXCHANGES)

        order_book = exchange_connector.get_order_book_sync(
            request.symbol, request.exchange, request.limit
        )

        return [
            TextContent(
                type="text",
                text=json.dumps(order_book, indent=2),
            )
        ]

    async def _handle_get_trades(self, arguments: dict) -> list[TextContent]:
        """Handle get_trades tool call"""
        request = TradesRequest(
            symbol=arguments["symbol"],
            limit=arguments.get("limit", 50),
            since=arguments.get("since"),
            exchange=arguments.get("exchange", config.DEFAULT_EXCHANGE),
        )

        validate_exchange(request.exchange, config.SUPPORTED_EXCHANGES)

        trades = exchange_connector.get_trades_sync(
            request.symbol, request.exchange, request.limit, request.since
        )

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "symbol": request.symbol,
                        "exchange": request.exchange,
                        "count": len(trades),
                        "trades": trades,
                    },
                    indent=2,
                ),
            )
        ]

    async def _handle_get_markets(self, arguments: dict) -> list[TextContent]:
        """Handle get_markets tool call"""
        request = MarketListRequest(
            exchange=arguments.get("exchange", config.DEFAULT_EXCHANGE),
            quote_currency=arguments.get("quote_currency"),
        )

        validate_exchange(request.exchange, config.SUPPORTED_EXCHANGES)

        markets = exchange_connector.get_markets(
            request.exchange, request.quote_currency
        )

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "exchange": request.exchange,
                        "quote_currency": request.quote_currency,
                        "count": len(markets),
                        "markets": markets[:100],  # Limit output size
                    },
                    indent=2,
                ),
            )
        ]

    async def _handle_clear_cache(self, arguments: dict) -> list[TextContent]:
        """Handle clear_cache tool call"""
        stats_before = cache_manager.get_stats()
        cache_manager.clear()
        stats_after = cache_manager.get_stats()

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "message": "Cache cleared successfully",
                        "before": stats_before,
                        "after": stats_after,
                    },
                    indent=2,
                ),
            )
        ]

    async def run(self) -> None:
        """Run the MCP server"""
        logger.info("Starting Crypto MCP Server...")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


async def main() -> None:
    """Main entry point"""
    server = CryptoMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
