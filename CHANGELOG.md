# Changelog

All notable changes to the Crypto MCP Server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-16

### Added
- Initial release of Crypto MCP Server
- MCP (Model Context Protocol) server implementation
- Support for 10+ major cryptocurrency exchanges via CCXT
- Real-time market data endpoints:
  - `get_ticker` - Current price and market data
  - `get_ohlcv` - Historical candlestick data
  - `get_order_book` - Market depth data
  - `get_trades` - Recent trade history
  - `get_markets` - Available trading pairs
- Intelligent caching with TTL support
- Rate limiting using sliding window algorithm
- Input validation using Pydantic models
- Comprehensive error handling and logging
- MCP resources for exchange info and cache statistics
- Complete test suite with 85%+ coverage
- Detailed documentation and examples
- CI/CD pipeline with GitHub Actions

### Features
- Multi-exchange support (Binance, Coinbase, Kraken, etc.)
- Configurable caching to reduce API calls
- Per-exchange rate limiting
- Type-safe request validation
- Structured logging with configurable levels
- Environment-based configuration
- Example usage scripts

### Technical
- Python 3.9+ support
- Async/await pattern for MCP protocol
- CCXT integration for exchange connectivity
- cachetools for TTL-based caching
- pytest with asyncio support for testing
- Black, isort, flake8 for code quality
- Type hints throughout codebase

### Documentation
- Comprehensive README with setup instructions
- API documentation for all tools
- Architecture overview and design decisions
- Contributing guidelines
- Usage examples
- Troubleshooting guide

### Testing
- Unit tests for all core modules
- Mock-based tests for external APIs
- Test fixtures for common data
- Coverage reporting
- Continuous integration

## [Unreleased]

### Planned Features
- WebSocket support for streaming data
- Database persistence for historical data
- Multi-exchange aggregation
- Technical indicators
- Portfolio tracking
- Alerts and notifications
- Docker containerization
- Prometheus metrics

---

## Version History

### Version 1.0.0 (2025-11-16)
**Initial Release** - Full-featured MCP server for cryptocurrency market data with comprehensive testing and documentation.

---

## Legend

- `Added` - New features
- `Changed` - Changes in existing functionality
- `Deprecated` - Soon-to-be removed features
- `Removed` - Removed features
- `Fixed` - Bug fixes
- `Security` - Security improvements
