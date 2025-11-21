"""
Cryptocurrency exchange connector using CCXT
"""

import ccxt
from typing import Dict, List, Optional, Any
from datetime import datetime
from .config import config
from .logger import logger
from .exceptions import (
    ExchangeConnectionError,
    ExchangeNotSupportedError,
    DataFetchError,
    InvalidSymbolError,
)
from .rate_limiter import rate_limiter
from .cache import cached


class ExchangeConnector:
    """Manages connections to cryptocurrency exchanges using CCXT"""

    def __init__(self):
        """Initialize exchange connector"""
        self._exchanges: Dict[str, ccxt.Exchange] = {}
        logger.info("ExchangeConnector initialized")

    def _get_exchange(self, exchange_name: str) -> ccxt.Exchange:
        """
        Get or create exchange instance.

        Args:
            exchange_name: Name of the exchange

        Returns:
            CCXT exchange instance

        Raises:
            ExchangeNotSupportedError: If exchange is not supported
            ExchangeConnectionError: If connection fails
        """
        exchange_name = exchange_name.lower()

        # Check if exchange is supported
        if exchange_name not in config.SUPPORTED_EXCHANGES:
            raise ExchangeNotSupportedError(
                f"Exchange '{exchange_name}' not supported. "
                f"Supported: {', '.join(config.SUPPORTED_EXCHANGES)}"
            )

        # Return existing instance if available
        if exchange_name in self._exchanges:
            return self._exchanges[exchange_name]

        # Create new exchange instance
        try:
            exchange_class = getattr(ccxt, exchange_name)
            credentials = config.get_exchange_credentials(exchange_name)

            # Initialize exchange with credentials if available
            exchange = exchange_class(
                {
                    "enableRateLimit": True,
                    "timeout": 30000,
                    **credentials,
                }
            )

            # Test connection
            exchange.load_markets()

            self._exchanges[exchange_name] = exchange
            logger.info(f"Connected to exchange: {exchange_name}")
            return exchange

        except AttributeError:
            raise ExchangeNotSupportedError(
                f"Exchange '{exchange_name}' not found in CCXT"
            )
        except Exception as e:
            logger.error(f"Failed to connect to {exchange_name}: {e}")
            raise ExchangeConnectionError(
                f"Failed to connect to {exchange_name}: {str(e)}"
            )

    @cached(key_prefix="ticker")
    async def get_ticker(self, symbol: str, exchange_name: str) -> Dict[str, Any]:
        """
        Get current ticker data for a symbol.

        Args:
            symbol: Trading pair (e.g., BTC/USDT)
            exchange_name: Exchange name

        Returns:
            Ticker data dictionary

        Raises:
            DataFetchError: If data fetch fails
        """
        try:
            rate_limiter.record_request(exchange_name)
            exchange = self._get_exchange(exchange_name)

            logger.debug(f"Fetching ticker for {symbol} on {exchange_name}")
            ticker = await exchange.fetch_ticker(symbol)

            return {
                "symbol": ticker.get("symbol", symbol),
                "exchange": exchange_name,
                "timestamp": ticker.get("timestamp"),
                "datetime": ticker.get("datetime"),
                "last": ticker.get("last"),
                "bid": ticker.get("bid"),
                "ask": ticker.get("ask"),
                "high": ticker.get("high"),
                "low": ticker.get("low"),
                "volume": ticker.get("baseVolume"),
                "quote_volume": ticker.get("quoteVolume"),
                "change": ticker.get("change"),
                "percentage": ticker.get("percentage"),
            }

        except ccxt.BadSymbol as e:
            raise InvalidSymbolError(f"Invalid symbol '{symbol}' on {exchange_name}: {e}")
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol} on {exchange_name}: {e}")
            raise DataFetchError(f"Failed to fetch ticker: {str(e)}")

    def get_ticker_sync(self, symbol: str, exchange_name: str) -> Dict[str, Any]:
        """Synchronous version of get_ticker"""
        try:
            rate_limiter.record_request(exchange_name)
            exchange = self._get_exchange(exchange_name)

            logger.debug(f"Fetching ticker for {symbol} on {exchange_name}")
            ticker = exchange.fetch_ticker(symbol)

            return {
                "symbol": ticker.get("symbol", symbol),
                "exchange": exchange_name,
                "timestamp": ticker.get("timestamp"),
                "datetime": ticker.get("datetime"),
                "last": ticker.get("last"),
                "bid": ticker.get("bid"),
                "ask": ticker.get("ask"),
                "high": ticker.get("high"),
                "low": ticker.get("low"),
                "volume": ticker.get("baseVolume"),
                "quote_volume": ticker.get("quoteVolume"),
                "change": ticker.get("change"),
                "percentage": ticker.get("percentage"),
            }

        except ccxt.BadSymbol as e:
            raise InvalidSymbolError(f"Invalid symbol '{symbol}' on {exchange_name}: {e}")
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol} on {exchange_name}: {e}")
            raise DataFetchError(f"Failed to fetch ticker: {str(e)}")

    @cached(key_prefix="ohlcv")
    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        exchange_name: str,
        limit: int = 100,
        since: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get OHLCV (candlestick) data.

        Args:
            symbol: Trading pair
            timeframe: Timeframe (e.g., 1m, 1h, 1d)
            exchange_name: Exchange name
            limit: Number of candles
            since: Start timestamp in milliseconds

        Returns:
            List of OHLCV candles

        Raises:
            DataFetchError: If data fetch fails
        """
        try:
            rate_limiter.record_request(exchange_name)
            exchange = self._get_exchange(exchange_name)

            logger.debug(
                f"Fetching OHLCV for {symbol} on {exchange_name} "
                f"(timeframe={timeframe}, limit={limit})"
            )
            ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, since, limit)

            return [
                {
                    "timestamp": candle[0],
                    "datetime": datetime.fromtimestamp(candle[0] / 1000).isoformat(),
                    "open": candle[1],
                    "high": candle[2],
                    "low": candle[3],
                    "close": candle[4],
                    "volume": candle[5],
                }
                for candle in ohlcv
            ]

        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol} on {exchange_name}: {e}")
            raise DataFetchError(f"Failed to fetch OHLCV data: {str(e)}")

    def get_ohlcv_sync(
        self,
        symbol: str,
        timeframe: str,
        exchange_name: str,
        limit: int = 100,
        since: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Synchronous version of get_ohlcv"""
        try:
            rate_limiter.record_request(exchange_name)
            exchange = self._get_exchange(exchange_name)

            logger.debug(
                f"Fetching OHLCV for {symbol} on {exchange_name} "
                f"(timeframe={timeframe}, limit={limit})"
            )
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)

            return [
                {
                    "timestamp": candle[0],
                    "datetime": datetime.fromtimestamp(candle[0] / 1000).isoformat(),
                    "open": candle[1],
                    "high": candle[2],
                    "low": candle[3],
                    "close": candle[4],
                    "volume": candle[5],
                }
                for candle in ohlcv
            ]

        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol} on {exchange_name}: {e}")
            raise DataFetchError(f"Failed to fetch OHLCV data: {str(e)}")

    async def get_order_book(
        self, symbol: str, exchange_name: str, limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get order book (depth) data.

        Args:
            symbol: Trading pair
            exchange_name: Exchange name
            limit: Depth of order book

        Returns:
            Order book data

        Raises:
            DataFetchError: If data fetch fails
        """
        try:
            rate_limiter.record_request(exchange_name)
            exchange = self._get_exchange(exchange_name)

            logger.debug(f"Fetching order book for {symbol} on {exchange_name}")
            order_book = await exchange.fetch_order_book(symbol, limit)

            return {
                "symbol": symbol,
                "exchange": exchange_name,
                "timestamp": order_book.get("timestamp"),
                "datetime": order_book.get("datetime"),
                "bids": [[price, amount] for price, amount in order_book["bids"][:limit]],
                "asks": [[price, amount] for price, amount in order_book["asks"][:limit]],
                "bid_count": len(order_book["bids"]),
                "ask_count": len(order_book["asks"]),
            }

        except Exception as e:
            logger.error(f"Error fetching order book for {symbol} on {exchange_name}: {e}")
            raise DataFetchError(f"Failed to fetch order book: {str(e)}")

    def get_order_book_sync(
        self, symbol: str, exchange_name: str, limit: int = 20
    ) -> Dict[str, Any]:
        """Synchronous version of get_order_book"""
        try:
            rate_limiter.record_request(exchange_name)
            exchange = self._get_exchange(exchange_name)

            logger.debug(f"Fetching order book for {symbol} on {exchange_name}")
            order_book = exchange.fetch_order_book(symbol, limit)

            return {
                "symbol": symbol,
                "exchange": exchange_name,
                "timestamp": order_book.get("timestamp"),
                "datetime": order_book.get("datetime"),
                "bids": [[price, amount] for price, amount in order_book["bids"][:limit]],
                "asks": [[price, amount] for price, amount in order_book["asks"][:limit]],
                "bid_count": len(order_book["bids"]),
                "ask_count": len(order_book["asks"]),
            }

        except Exception as e:
            logger.error(f"Error fetching order book for {symbol} on {exchange_name}: {e}")
            raise DataFetchError(f"Failed to fetch order book: {str(e)}")

    async def get_trades(
        self,
        symbol: str,
        exchange_name: str,
        limit: int = 50,
        since: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get recent trades.

        Args:
            symbol: Trading pair
            exchange_name: Exchange name
            limit: Number of trades
            since: Start timestamp in milliseconds

        Returns:
            List of recent trades

        Raises:
            DataFetchError: If data fetch fails
        """
        try:
            rate_limiter.record_request(exchange_name)
            exchange = self._get_exchange(exchange_name)

            logger.debug(f"Fetching trades for {symbol} on {exchange_name}")
            trades = await exchange.fetch_trades(symbol, since, limit)

            return [
                {
                    "id": trade.get("id"),
                    "timestamp": trade.get("timestamp"),
                    "datetime": trade.get("datetime"),
                    "symbol": trade.get("symbol", symbol),
                    "type": trade.get("type"),
                    "side": trade.get("side"),
                    "price": trade.get("price"),
                    "amount": trade.get("amount"),
                    "cost": trade.get("cost"),
                }
                for trade in trades
            ]

        except Exception as e:
            logger.error(f"Error fetching trades for {symbol} on {exchange_name}: {e}")
            raise DataFetchError(f"Failed to fetch trades: {str(e)}")

    def get_trades_sync(
        self,
        symbol: str,
        exchange_name: str,
        limit: int = 50,
        since: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Synchronous version of get_trades"""
        try:
            rate_limiter.record_request(exchange_name)
            exchange = self._get_exchange(exchange_name)

            logger.debug(f"Fetching trades for {symbol} on {exchange_name}")
            trades = exchange.fetch_trades(symbol, since, limit)

            return [
                {
                    "id": trade.get("id"),
                    "timestamp": trade.get("timestamp"),
                    "datetime": trade.get("datetime"),
                    "symbol": trade.get("symbol", symbol),
                    "type": trade.get("type"),
                    "side": trade.get("side"),
                    "price": trade.get("price"),
                    "amount": trade.get("amount"),
                    "cost": trade.get("cost"),
                }
                for trade in trades
            ]

        except Exception as e:
            logger.error(f"Error fetching trades for {symbol} on {exchange_name}: {e}")
            raise DataFetchError(f"Failed to fetch trades: {str(e)}")

    @cached(key_prefix="markets")
    def get_markets(
        self, exchange_name: str, quote_currency: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get list of available markets on an exchange.

        Args:
            exchange_name: Exchange name
            quote_currency: Filter by quote currency (e.g., USDT)

        Returns:
            List of markets

        Raises:
            DataFetchError: If data fetch fails
        """
        try:
            exchange = self._get_exchange(exchange_name)

            logger.debug(f"Fetching markets for {exchange_name}")
            markets = exchange.load_markets()

            result = []
            for symbol, market in markets.items():
                # Filter by quote currency if specified
                if quote_currency and market.get("quote") != quote_currency.upper():
                    continue

                result.append(
                    {
                        "symbol": symbol,
                        "base": market.get("base"),
                        "quote": market.get("quote"),
                        "active": market.get("active", True),
                        "type": market.get("type"),
                        "spot": market.get("spot", False),
                        "margin": market.get("margin", False),
                        "future": market.get("future", False),
                        "swap": market.get("swap", False),
                    }
                )

            logger.info(f"Found {len(result)} markets on {exchange_name}")
            return result

        except Exception as e:
            logger.error(f"Error fetching markets for {exchange_name}: {e}")
            raise DataFetchError(f"Failed to fetch markets: {str(e)}")

    def close(self, exchange_name: Optional[str] = None) -> None:
        """
        Close exchange connection(s).

        Args:
            exchange_name: Specific exchange to close, or None to close all
        """
        if exchange_name:
            if exchange_name in self._exchanges:
                del self._exchanges[exchange_name]
                logger.info(f"Closed connection to {exchange_name}")
        else:
            self._exchanges.clear()
            logger.info("Closed all exchange connections")


# Global exchange connector instance
exchange_connector = ExchangeConnector()
