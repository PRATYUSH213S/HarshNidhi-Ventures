# Crypto MCP Server

A Python-based Model Context Protocol (MCP) server for retrieving real-time and historical cryptocurrency market data from major exchanges using CCXT.

## 🌟 Features

### Core MCP Capabilities
- **Real-time Market Data**: Current ticker prices, order books, and recent trades
- **Historical Data**: OHLCV (candlestick) data with customizable timeframes
- **Multi-Exchange Support**: Connect to 10+ major cryptocurrency exchanges
- **Market Discovery**: List available trading pairs on any supported exchange

### Performance & Reliability
- **Intelligent Caching**: TTL-based caching to reduce API calls and improve response times
- **Rate Limiting**: Sliding window rate limiter to prevent API quota exhaustion
- **Error Handling**: Comprehensive error handling with detailed logging
- **Input Validation**: Pydantic-based request validation for data integrity

### Supported Exchanges
- Binance
- Coinbase
- Kraken
- Bitfinex
- Bitstamp
- Gemini
- KuCoin
- OKX
- Bybit
- Gate.io

## 📋 Table of Contents
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Architecture](#architecture)
- [Assumptions & Design Decisions](#assumptions--design-decisions)
- [Contributing](#contributing)

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Git (for cloning the repository)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/crypto-mcp-server.git
   cd crypto-mcp-server
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your API keys (optional for most exchanges)
   ```

## ⚙️ Configuration

### Environment Variables

The server can be configured using a `.env` file. Copy `.env.example` to `.env` and customize:

```env
# API Keys (optional - only needed for private endpoints)
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret

# Server Configuration
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR, CRITICAL
CACHE_TTL=60                    # Cache time-to-live in seconds
RATE_LIMIT_REQUESTS=10          # Max requests per time window
RATE_LIMIT_PERIOD=60            # Time window in seconds

# Default Exchange
DEFAULT_EXCHANGE=binance        # Default exchange for queries
```

### Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging verbosity level |
| `CACHE_TTL` | `60` | Cache expiration time (seconds) |
| `RATE_LIMIT_REQUESTS` | `10` | Maximum requests per period |
| `RATE_LIMIT_PERIOD` | `60` | Rate limit time window (seconds) |
| `DEFAULT_EXCHANGE` | `binance` | Default exchange when not specified |

## 📖 Usage

### Starting the Server

Run the MCP server using:

```bash
python main.py
```

Or using the module directly:

```bash
python -m crypto_mcp_server.server
```

### MCP Integration

The server implements the Model Context Protocol and can be integrated with MCP-compatible clients. It communicates via stdio using the MCP protocol.


         


## 📚 API Documentation

### Available Tools

#### 1. get_ticker
Get current price and market data for a cryptocurrency pair.

**Parameters:**
- `symbol` (required): Trading pair (e.g., "BTC/USDT")
- `exchange` (optional): Exchange name (default: binance)

**Example:**
```json
{
  "symbol": "BTC/USDT",
  "exchange": "binance"
}
```

**Response:**
```json
{
  "symbol": "BTC/USDT",
  "exchange": "binance",
  "timestamp": 1700000000000,
  "last": 37000.0,
  "bid": 36999.5,
  "ask": 37000.5,
  "high": 37500.0,
  "low": 36500.0,
  "volume": 1234.56,
  "percentage": 1.37
}
```

#### 2. get_ohlcv
Get historical OHLCV (candlestick) data.

**Parameters:**
- `symbol` (required): Trading pair
- `timeframe` (optional): Candle timeframe (default: "1h")
  - Valid: 1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 12h, 1d, 1w
- `limit` (optional): Number of candles (default: 100, max: 1000)
- `since` (optional): Start timestamp in milliseconds
- `exchange` (optional): Exchange name

**Example:**
```json
{
  "symbol": "ETH/USDT",
  "timeframe": "1h",
  "limit": 24,
  "exchange": "binance"
}
```

**Response:**
```json
{
  "symbol": "ETH/USDT",
  "exchange": "binance",
  "timeframe": "1h",
  "count": 24,
  "data": [
    {
      "timestamp": 1700000000000,
      "datetime": "2023-11-14T00:00:00",
      "open": 2000.0,
      "high": 2050.0,
      "low": 1990.0,
      "close": 2030.0,
      "volume": 1000.0
    }
  ]
}
```

#### 3. get_order_book
Get current order book (market depth) data.

**Parameters:**
- `symbol` (required): Trading pair
- `limit` (optional): Depth of order book (default: 20, max: 100)
- `exchange` (optional): Exchange name

**Example:**
```json
{
  "symbol": "BTC/USDT",
  "limit": 10,
  "exchange": "binance"
}
```

**Response:**
```json
{
  "symbol": "BTC/USDT",
  "exchange": "binance",
  "timestamp": 1700000000000,
  "bids": [[37000.0, 1.5], [36999.0, 2.0]],
  "asks": [[37001.0, 1.2], [37002.0, 1.8]],
  "bid_count": 10,
  "ask_count": 10
}
```

#### 4. get_trades
Get recent trades for a trading pair.

**Parameters:**
- `symbol` (required): Trading pair
- `limit` (optional): Number of trades (default: 50, max: 500)
- `since` (optional): Start timestamp in milliseconds
- `exchange` (optional): Exchange name

**Example:**
```json
{
  "symbol": "BTC/USDT",
  "limit": 10,
  "exchange": "binance"
}
```

#### 5. get_markets
Get list of available trading pairs on an exchange.

**Parameters:**
- `exchange` (optional): Exchange name
- `quote_currency` (optional): Filter by quote currency (e.g., "USDT")

**Example:**
```json
{
  "exchange": "binance",
  "quote_currency": "USDT"
}
```

#### 6. clear_cache
Clear the server's cache.

**Parameters:** None

### Available Resources

#### crypto://exchanges
List of supported exchanges and default configuration.

#### crypto://cache/stats
Current cache performance statistics including hit rate and size.

## 🧪 Testing

### Running Tests

Run the complete test suite:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=crypto_mcp_server --cov-report=html

# Run specific test file
pytest tests/test_validators.py

# Run with verbose output
pytest -v

# Run tests in parallel (faster)
pytest -n auto
```

### Test Coverage

The project includes comprehensive test coverage for:

- ✅ **Validators**: Input validation and Pydantic models
- ✅ **Cache Manager**: Caching operations and TTL behavior
- ✅ **Rate Limiter**: Sliding window algorithm and quotas
- ✅ **Exchange Connector**: CCXT integration and data fetching
- ✅ **MCP Server**: Tool handlers and resource endpoints
- ✅ **Error Handling**: Exception handling and edge cases

**Target Coverage**: 85%+ code coverage across all modules.

### Test Structure

```
tests/
├── __init__.py
├── conftest.py           # Shared fixtures
├── test_validators.py    # Validation tests
├── test_cache.py         # Cache functionality tests
├── test_rate_limiter.py  # Rate limiting tests
├── test_exchange.py      # Exchange connector tests
└── test_server.py        # MCP server tests
```

## 🏗️ Architecture

### Project Structure

```
crypto-mcp-server/
├── crypto_mcp_server/
│   ├── __init__.py          # Package initialization
│   ├── server.py            # Main MCP server implementation
│   ├── exchange.py          # CCXT exchange connector
│   ├── cache.py             # Caching utilities
│   ├── rate_limiter.py      # Rate limiting
│   ├── validators.py        # Input validation
│   ├── config.py            # Configuration management
│   ├── logger.py            # Logging utilities
│   └── exceptions.py        # Custom exceptions
├── tests/                   # Test suite
├── main.py                  # Entry point
├── pyproject.toml           # Project metadata
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

### Component Overview

#### 1. MCP Server (`server.py`)
- Implements Model Context Protocol
- Handles tool calls and resource requests
- Orchestrates data fetching and validation

#### 2. Exchange Connector (`exchange.py`)
- CCXT integration for exchange communication
- Unified interface for multiple exchanges
- Connection pooling and reuse

#### 3. Cache Manager (`cache.py`)
- TTL-based caching using `cachetools`
- Automatic expiration and cleanup
- Hit rate tracking

#### 4. Rate Limiter (`rate_limiter.py`)
- Sliding window algorithm
- Per-exchange rate limiting
- Prevents API quota exhaustion

#### 5. Validators (`validators.py`)
- Pydantic-based input validation
- Type checking and conversion
- Request sanitization

### Data Flow

```
Client Request
    ↓
MCP Server (server.py)
    ↓
Input Validation (validators.py)
    ↓
Rate Limit Check (rate_limiter.py)
    ↓
Cache Check (cache.py)
    ↓ (if miss)
Exchange Connector (exchange.py)
    ↓
CCXT Library
    ↓
Exchange API
    ↓
Cache Store (cache.py)
    ↓
Response to Client
```

## 🤔 Assumptions & Design Decisions

### 1. Exchange Selection
- **Assumption**: Binance is the default exchange due to its high liquidity and comprehensive API
- **Rationale**: Provides best experience for users without explicit exchange preference
- **Impact**: Can be overridden per-request via the `exchange` parameter

### 2. Caching Strategy
- **Assumption**: Market data has a reasonable staleness tolerance (60s default)
- **Rationale**: Reduces API load and improves response time for repeated queries
- **Impact**: Data may be up to 60 seconds old; configurable via `CACHE_TTL`

### 3. Rate Limiting
- **Assumption**: Default of 10 requests per 60 seconds is conservative
- **Rationale**: Prevents hitting exchange rate limits while allowing reasonable usage
- **Impact**: May need adjustment based on exchange-specific limits

### 4. Synchronous Exchange Calls
- **Assumption**: Synchronous CCXT calls are acceptable for the server
- **Rationale**: Simpler implementation; CCXT's async support varies by exchange
- **Impact**: Server uses sync methods with async handlers for MCP protocol

### 5. No Authentication Required
- **Assumption**: Public market data doesn't require API keys
- **Rationale**: Makes setup easier; most exchanges provide public market data
- **Impact**: API keys only needed for private/authenticated endpoints

### 6. Error Propagation
- **Assumption**: Errors should be descriptive but not expose sensitive details
- **Rationale**: Helps debugging while maintaining security
- **Impact**: Custom exception hierarchy with sanitized messages

### 7. Market Data Only
- **Assumption**: Server focuses on market data, not trading operations
- **Rationale**: Aligns with "data retrieval" requirement; reduces complexity
- **Impact**: No order placement or account management features

### 8. UTC Timestamps
- **Assumption**: All timestamps are in UTC and milliseconds
- **Rationale**: Standard for cryptocurrency exchanges; unambiguous
- **Impact**: Client must handle timezone conversion if needed

### 9. Symbol Format
- **Assumption**: Symbols use base/quote format (e.g., BTC/USDT)
- **Rationale**: CCXT standard format across exchanges
- **Impact**: Clients must use slash-separated pairs

### 10. Testing Strategy
- **Assumption**: Mocking external APIs is acceptable for unit tests
- **Rationale**: Fast, reliable tests without network dependencies
- **Impact**: Integration tests with live exchanges not included

## 🔧 Troubleshooting

### Common Issues

**Issue**: Exchange connection fails
- **Solution**: Check if exchange is in `SUPPORTED_EXCHANGES` list
- **Solution**: Verify internet connection and exchange API status

**Issue**: Rate limit errors
- **Solution**: Increase `RATE_LIMIT_PERIOD` or decrease request frequency
- **Solution**: Check exchange-specific rate limits

**Issue**: Symbol not found
- **Solution**: Verify symbol format (e.g., BTC/USDT, not BTCUSDT)
- **Solution**: Use `get_markets` tool to list available symbols

**Issue**: Stale data
- **Solution**: Decrease `CACHE_TTL` for fresher data
- **Solution**: Use `clear_cache` tool to flush cache

## 📈 Performance Optimization

### Recommended Settings

For high-frequency queries:
```env
CACHE_TTL=30
RATE_LIMIT_REQUESTS=20
```

For reduced API usage:
```env
CACHE_TTL=120
RATE_LIMIT_REQUESTS=5
```

For real-time data:
```env
CACHE_TTL=5
RATE_LIMIT_REQUESTS=30
```

## 🚀 Future Enhancements

Potential improvements for future versions:

- [ ] WebSocket support for real-time streaming data
- [ ] Database persistence for historical data
- [ ] Multi-exchange aggregation and arbitrage detection
- [ ] Advanced technical indicators
- [ ] Portfolio tracking capabilities
- [ ] Alerts and notifications
- [ ] GraphQL API layer
- [ ] Docker containerization
- [ ] Kubernetes deployment configs
- [ ] Prometheus metrics exporter

## 📄 License

This project is licensed under the MIT License.

## 👥 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Write tests for new features
- Maintain code coverage above 80%
- Follow PEP 8 style guide
- Use type hints
- Update documentation

## 📞 Support

For issues, questions, or contributions:
- Create an issue on GitHub
- Contact: prat27703@gmail.com
## 🙏 Acknowledgments

- **CCXT**: Cryptocurrency trading library
- **MCP**: Model Context Protocol specification
- **Pydantic**: Data validation library
- **pytest**: Testing framework

---

**Built with ❤️ for HarshNidhi Ventures**

*Last Updated: November 21, 2025*
