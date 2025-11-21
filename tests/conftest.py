"""
Test configuration and fixtures
"""

import pytest
from crypto_mcp_server.config import config


@pytest.fixture
def sample_ticker_data():
    """Sample ticker data for testing"""
    return {
        "symbol": "BTC/USDT",
        "timestamp": 1700000000000,
        "datetime": "2023-11-14T00:00:00.000Z",
        "last": 37000.0,
        "bid": 36999.5,
        "ask": 37000.5,
        "high": 37500.0,
        "low": 36500.0,
        "volume": 1234.56,
        "quote_volume": 45678900.0,
        "change": 500.0,
        "percentage": 1.37,
    }


@pytest.fixture
def sample_ohlcv_data():
    """Sample OHLCV data for testing"""
    return [
        [1700000000000, 37000.0, 37500.0, 36500.0, 37200.0, 100.0],
        [1700003600000, 37200.0, 37800.0, 37100.0, 37600.0, 120.0],
        [1700007200000, 37600.0, 38000.0, 37400.0, 37800.0, 110.0],
    ]


@pytest.fixture
def sample_order_book_data():
    """Sample order book data for testing"""
    return {
        "symbol": "BTC/USDT",
        "timestamp": 1700000000000,
        "datetime": "2023-11-14T00:00:00.000Z",
        "bids": [[37000.0, 1.5], [36999.0, 2.0], [36998.0, 1.0]],
        "asks": [[37001.0, 1.2], [37002.0, 1.8], [37003.0, 2.5]],
    }


@pytest.fixture
def sample_trades_data():
    """Sample trades data for testing"""
    return [
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
        },
        {
            "id": "12346",
            "timestamp": 1700000001000,
            "datetime": "2023-11-14T00:00:01.000Z",
            "symbol": "BTC/USDT",
            "type": "market",
            "side": "sell",
            "price": 37000.5,
            "amount": 0.3,
            "cost": 11100.15,
        },
    ]


@pytest.fixture
def sample_markets_data():
    """Sample markets data for testing"""
    return {
        "BTC/USDT": {
            "id": "BTCUSDT",
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
            "id": "ETHUSDT",
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
