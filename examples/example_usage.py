"""
Example usage of the Crypto MCP Server with MCP client
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def demonstrate_crypto_mcp():
    """Demonstrate various features of the Crypto MCP Server"""

    print("=" * 60)
    print("Crypto MCP Server - Usage Examples")
    print("=" * 60)

    # Configure server parameters
    server_params = StdioServerParameters(
        command="python", args=["main.py"], env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize session
            await session.initialize()
            print("\n✓ Session initialized successfully\n")

            # Example 1: List available resources
            print("1. Listing Available Resources")
            print("-" * 60)
            resources = await session.list_resources()
            for resource in resources:
                print(f"   - {resource.name}: {resource.uri}")
            print()

            # Example 2: List available tools
            print("2. Listing Available Tools")
            print("-" * 60)
            tools = await session.list_tools()
            for tool in tools:
                print(f"   - {tool.name}: {tool.description}")
            print()

            # Example 3: Get ticker data
            print("3. Getting BTC/USDT Ticker from Binance")
            print("-" * 60)
            ticker_result = await session.call_tool(
                "get_ticker", arguments={"symbol": "BTC/USDT", "exchange": "binance"}
            )
            ticker_data = json.loads(ticker_result[0].text)
            print(f"   Symbol: {ticker_data.get('symbol')}")
            print(f"   Last Price: ${ticker_data.get('last'):,.2f}")
            print(f"   24h Change: {ticker_data.get('percentage'):.2f}%")
            print(f"   24h High: ${ticker_data.get('high'):,.2f}")
            print(f"   24h Low: ${ticker_data.get('low'):,.2f}")
            print()

            # Example 4: Get OHLCV data
            print("4. Getting ETH/USDT 1h Candles (last 5)")
            print("-" * 60)
            ohlcv_result = await session.call_tool(
                "get_ohlcv",
                arguments={
                    "symbol": "ETH/USDT",
                    "timeframe": "1h",
                    "limit": 5,
                    "exchange": "binance",
                },
            )
            ohlcv_data = json.loads(ohlcv_result[0].text)
            for i, candle in enumerate(ohlcv_data["data"][-3:], 1):
                print(f"   Candle {i}:")
                print(f"      Time: {candle['datetime']}")
                print(
                    f"      OHLC: ${candle['open']:.2f} / ${candle['high']:.2f} / "
                    f"${candle['low']:.2f} / ${candle['close']:.2f}"
                )
            print()

            # Example 5: Get order book
            print("5. Getting BTC/USDT Order Book (top 3 levels)")
            print("-" * 60)
            orderbook_result = await session.call_tool(
                "get_order_book",
                arguments={"symbol": "BTC/USDT", "limit": 3, "exchange": "binance"},
            )
            orderbook_data = json.loads(orderbook_result[0].text)
            print("   Asks (Sell Orders):")
            for price, amount in orderbook_data["asks"][:3]:
                print(f"      ${price:,.2f} - {amount:.4f} BTC")
            print("   Bids (Buy Orders):")
            for price, amount in orderbook_data["bids"][:3]:
                print(f"      ${price:,.2f} - {amount:.4f} BTC")
            print()

            # Example 6: Get recent trades
            print("6. Getting Recent BTC/USDT Trades (last 3)")
            print("-" * 60)
            trades_result = await session.call_tool(
                "get_trades",
                arguments={"symbol": "BTC/USDT", "limit": 3, "exchange": "binance"},
            )
            trades_data = json.loads(trades_result[0].text)
            for trade in trades_data["trades"][:3]:
                print(f"   {trade['datetime']}:")
                print(
                    f"      {trade['side'].upper()} {trade['amount']:.4f} BTC @ "
                    f"${trade['price']:,.2f}"
                )
            print()

            # Example 7: List USDT markets
            print("7. Listing USDT Markets on Binance (first 5)")
            print("-" * 60)
            markets_result = await session.call_tool(
                "get_markets",
                arguments={"exchange": "binance", "quote_currency": "USDT"},
            )
            markets_data = json.loads(markets_result[0].text)
            for market in markets_data["markets"][:5]:
                status = "✓" if market["active"] else "✗"
                print(f"   {status} {market['symbol']} ({market['type']})")
            print(f"   ... and {markets_data['count'] - 5} more markets")
            print()

            # Example 8: Read resource
            print("8. Reading Supported Exchanges Resource")
            print("-" * 60)
            exchanges_resource = await session.read_resource("crypto://exchanges")
            exchanges_data = json.loads(exchanges_resource[0].text)
            print(f"   Default Exchange: {exchanges_data['default_exchange']}")
            print(
                f"   Supported: {', '.join(exchanges_data['supported_exchanges'][:5])}..."
            )
            print()

            # Example 9: Cache statistics
            print("9. Cache Performance Statistics")
            print("-" * 60)
            cache_resource = await session.read_resource("crypto://cache/stats")
            cache_data = json.loads(cache_resource[0].text)
            print(f"   Cache Hits: {cache_data['hits']}")
            print(f"   Cache Misses: {cache_data['misses']}")
            print(f"   Hit Rate: {cache_data['hit_rate_percent']:.1f}%")
            print(f"   Current Size: {cache_data['current_size']}/{cache_data['max_size']}")
            print()

            print("=" * 60)
            print("✓ All examples completed successfully!")
            print("=" * 60)


async def main():
    """Main entry point"""
    try:
        await demonstrate_crypto_mcp()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("\nStarting Crypto MCP Server examples...")
    print("Make sure the server is configured correctly.\n")
    asyncio.run(main())
