"""
Simple example demonstrating basic MCP server usage
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def simple_example():
    """Simple example of getting Bitcoin price"""

    # Configure server
    server_params = StdioServerParameters(command="python", args=["main.py"])

    # Connect to server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()

            # Get BTC price
            result = await session.call_tool(
                "get_ticker", arguments={"symbol": "BTC/USDT"}
            )

            # Parse result
            import json

            data = json.loads(result[0].text)

            # Display
            print(f"\n{'=' * 50}")
            print(f"Bitcoin (BTC) Current Price")
            print(f"{'=' * 50}")
            print(f"Price: ${data['last']:,.2f}")
            print(f"24h Change: {data['percentage']:+.2f}%")
            print(f"24h High: ${data['high']:,.2f}")
            print(f"24h Low: ${data['low']:,.2f}")
            print(f"{'=' * 50}\n")


if __name__ == "__main__":
    asyncio.run(simple_example())
