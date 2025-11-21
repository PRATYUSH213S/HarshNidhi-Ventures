📌 Crypto MCP Server

A lightweight yet production-oriented Python MCP server that delivers real-time and historical cryptocurrency market data using CCXT, with a fully functional Mock mode, async architecture, caching, and clean tooling.

🌟 Key Features (Simplified)
🔹 Core MCP Tools

get_ticker → real-time price, spread, volume

get_ohlcv → historical candlestick data

get_markets → list trading pairs

get_trades → recent trades

get_order_book → order book depth

clear_cache → flush server cache

🔹 Exchange Support

Connects to major exchanges via CCXT (Binance, Coinbase, Kraken, Bitfinex, Bybit, KuCoin, OKX, etc.)
Mock exchange included for offline development.

🔹 Performance

TTL caching to avoid redundant API calls

Rate limiting to prevent quota exhaustion

Fast async handlers

Error-safe exception system

🔹 Developer Friendly

Pydantic validation

Clean folder structure

Logging utilities

Complete pytest suite (no external network calls)

🚀 Installation (Quick)
git clone https://github.com/yourusername/crypto-mcp-server.git
cd crypto-mcp-server

python -m venv venv
source venv/bin/activate     # or venv\Scripts\activate

pip install -r requirements.txt


Run the server:

python main.py


or via module:

python -m crypto_mcp_server.server

📚 MCP Usage Example
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()

        result = await session.call_tool(
            "get_ticker",
            {"symbol": "BTC/USDT", "exchange": "binance"}
        )
        print(result)

📡 Available Tools (Short Summary)
Tool	Description
get_ticker	Live market price & stats
get_ohlcv	Historical OHLCV candles
get_order_book	Bid/ask market depth
get_trades	Recent trades
get_markets	List all symbols
clear_cache	Clears cache
🧪 Testing
pytest
pytest --cov=crypto_mcp_server


Includes tests for:

validators

cache

rate limiter

exchange connector

MCP tools

error handling

🏗 Architecture (Short View)
MCP Server
 ├── Tools
 ├── Validators
 ├── Rate Limiter
 ├── Cache Manager
 ├── Exchange Connector (CCXT)
 └── Exceptions & Logging

🤔 Key Design Assumptions

Public market data → no API keys required

CCXT used as unified interface

TTL caching reduces rate limits

Mock exchange makes tests reliable

UTC timestamps everywhere

🔮 Future Enhancements

WebSocket push updates

Persistent DB for OHLCV

More advanced indicators

Docker + Kubernetes deployment

Prometheus & monitoring hooks

❤️ Credits

Built with FastAPI, CCXT, Pydantic, pytest & MCP spec
