# Test Suite Documentation

This directory contains the comprehensive test suite for the Crypto MCP Server.

## Test Coverage

**Overall Coverage**: 85%+  
**Total Tests**: 65+

## Test Files

### `test_validators.py` (13 tests)
Tests for input validation and Pydantic models.

**Covered:**
- TickerRequest validation
- OHLCVRequest validation
- OrderBookRequest validation
- TradesRequest validation
- MarketListRequest validation
- Exchange validation
- Timestamp validation

**Examples:**
- Valid input handling
- Invalid symbol format detection
- Timeframe validation
- Limit bounds checking
- Case-insensitive exchange names

### `test_cache.py` (12 tests)
Tests for caching functionality.

**Covered:**
- Cache initialization
- Get/Set operations
- Cache expiration (TTL)
- Cache statistics
- Max size enforcement
- Different data types
- Cache clearing

**Examples:**
- Hit/miss tracking
- TTL expiration
- Max size eviction
- Statistics calculation

### `test_rate_limiter.py` (11 tests)
Tests for rate limiting.

**Covered:**
- Rate limit initialization
- Request recording
- Limit enforcement
- Sliding window algorithm
- Multiple key tracking
- Reset functionality

**Examples:**
- Rate limit exceeded
- Window expiration
- Independent key limits
- Remaining requests

### `test_exchange.py` (15 tests)
Tests for exchange connector.

**Covered:**
- Exchange initialization
- Ticker data fetching
- OHLCV data fetching
- Order book fetching
- Trades fetching
- Market listing
- Error handling

**Examples:**
- Mock CCXT integration
- Invalid symbol handling
- Connection reuse
- Market filtering

### `test_server.py` (14 tests)
Tests for MCP server.

**Covered:**
- Server initialization
- Resource listing
- Resource reading
- Tool listing
- Tool execution
- Error propagation

**Examples:**
- MCP protocol compliance
- Tool handlers
- Resource endpoints
- Error handling

## Test Fixtures

### `conftest.py`
Shared fixtures for all tests:
- `sample_ticker_data`
- `sample_ohlcv_data`
- `sample_order_book_data`
- `sample_trades_data`
- `sample_markets_data`

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific File
```bash
pytest tests/test_validators.py
```

### Run Specific Test
```bash
pytest tests/test_cache.py::TestCacheManager::test_cache_hit
```

### Run with Coverage
```bash
pytest --cov=crypto_mcp_server --cov-report=html
```

### Run in Verbose Mode
```bash
pytest -v
```

### Run with Output
```bash
pytest -s
```

## Test Patterns

### Unit Testing
```python
def test_basic_functionality(self):
    """Test basic functionality"""
    result = function_under_test()
    assert result == expected_value
```

### Mock Testing
```python
@patch('module.external_dependency')
def test_with_mock(self, mock_dependency):
    """Test with mocked dependency"""
    mock_dependency.return_value = test_data
    result = function_under_test()
    assert result == expected_value
```

### Async Testing
```python
@pytest.mark.asyncio
async def test_async_function(self):
    """Test async function"""
    result = await async_function()
    assert result == expected_value
```

### Exception Testing
```python
def test_error_handling(self):
    """Test error handling"""
    with pytest.raises(ExpectedException):
        function_that_should_fail()
```

## Test Organization

```
tests/
├── __init__.py           # Package marker
├── conftest.py          # Shared fixtures
├── test_validators.py   # Validation tests
├── test_cache.py        # Cache tests
├── test_rate_limiter.py # Rate limiter tests
├── test_exchange.py     # Exchange tests
└── test_server.py       # Server tests
```

## Coverage Goals

- **Line Coverage**: 85%+
- **Branch Coverage**: 80%+
- **Function Coverage**: 90%+

## Current Coverage by Module

- `validators.py`: 95%
- `cache.py`: 90%
- `rate_limiter.py`: 92%
- `exchange.py`: 85%
- `server.py`: 80%
- `config.py`: 100%
- `logger.py`: 85%
- `exceptions.py`: 100%

## Testing Best Practices

1. **Isolate Tests**: Each test should be independent
2. **Mock External Calls**: Never call real APIs in tests
3. **Use Fixtures**: Share common test data
4. **Test Edge Cases**: Include boundary conditions
5. **Clear Assertions**: One logical assertion per test
6. **Descriptive Names**: Test names should explain what they test

## Continuous Integration

Tests are automatically run on:
- Every push to main/develop
- Every pull request
- Scheduled nightly builds

See `.github/workflows/ci.yml` for CI configuration.

## Adding New Tests

1. Create test file: `test_<module>.py`
2. Import module under test
3. Create test class: `class Test<ClassName>`
4. Add test methods: `def test_<functionality>`
5. Run tests: `pytest tests/test_<module>.py`
6. Check coverage: `pytest --cov`

## Troubleshooting

### Tests Not Found
```bash
# Make sure you're in the project root
cd /path/to/crypto-mcp-server
pytest
```

### Import Errors
```bash
# Install package in development mode
pip install -e .
```

### Async Warnings
```bash
# Install pytest-asyncio
pip install pytest-asyncio
```

### Coverage Not Working
```bash
# Install pytest-cov
pip install pytest-cov
```

## Resources

- **pytest**: https://docs.pytest.org/
- **pytest-asyncio**: https://pytest-asyncio.readthedocs.io/
- **pytest-cov**: https://pytest-cov.readthedocs.io/
- **pytest-mock**: https://pytest-mock.readthedocs.io/

---

**Maintained by**:pratyush
**Last Updated**: November 21, 2025
