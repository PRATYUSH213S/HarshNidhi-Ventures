# Crypto MCP Server - Quick Reference

Quick reference guide for the Crypto MCP Server.

## Installation

```bash
git clone <repository-url>
cd crypto-mcp-server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

## MCP Tools

### get_ticker
Get current price data.
```json
{"symbol": "BTC/USDT", "exchange": "binance"}
```

### get_ohlcv
Get historical candlestick data.
```json
{
  "symbol": "ETH/USDT",
  "timeframe": "1h",
  "limit": 100,
  "exchange": "binance"
}
```

### get_order_book
Get market depth.
```json
{"symbol": "BTC/USDT", "limit": 20, "exchange": "binance"}
```

### get_trades
Get recent trades.
```json
{"symbol": "BTC/USDT", "limit": 50, "exchange": "binance"}
```

### get_markets
List available trading pairs.
```json
{"exchange": "binance", "quote_currency": "USDT"}
```

### clear_cache
Clear server cache.
```json
{}
```

## MCP Resources

- `crypto://exchanges` - Supported exchanges list
- `crypto://cache/stats` - Cache performance stats

## Supported Exchanges

binance, coinbase, kraken, bitfinex, bitstamp, gemini, kucoin, okx, bybit, gate

## Timeframes

1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 12h, 1d, 1w

## Symbol Format

Use base/quote format: `BTC/USDT`, `ETH/BTC`, etc.

## Environment Variables

```env
LOG_LEVEL=INFO
CACHE_TTL=60
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_PERIOD=60
DEFAULT_EXCHANGE=binance
```

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=crypto_mcp_server

# Specific test
pytest tests/test_validators.py
```

## Common Commands

```bash
# Format code
black crypto_mcp_server tests

# Sort imports
isort crypto_mcp_server tests

# Lint
flake8 crypto_mcp_server tests --max-line-length=100

# Type check
mypy crypto_mcp_server
```

## Troubleshooting

**Rate limit error**: Increase `RATE_LIMIT_PERIOD` or reduce request frequency

**Symbol not found**: Use `get_markets` to list available symbols

**Stale data**: Decrease `CACHE_TTL` or use `clear_cache`

**Exchange connection failed**: Check exchange is in supported list

## Quick Example

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def get_btc_price():
    server_params = StdioServerParameters(
        command="python", args=["main.py"]
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "get_ticker",
                arguments={"symbol": "BTC/USDT"}
            )
            print(result[0].text)

asyncio.run(get_btc_price())
```

## Performance Tips

**High-frequency**: `CACHE_TTL=30, RATE_LIMIT_REQUESTS=20`

**Low API usage**: `CACHE_TTL=120, RATE_LIMIT_REQUESTS=5`

**Real-time**: `CACHE_TTL=5, RATE_LIMIT_REQUESTS=30`

## Project Structure

```
crypto_mcp_server/
├── server.py          # MCP server
├── exchange.py        # Exchange connector
├── cache.py           # Caching
├── rate_limiter.py    # Rate limiting
├── validators.py      # Input validation
├── config.py          # Configuration
├── logger.py          # Logging
└── exceptions.py      # Custom exceptions
```

