"""
Custom exceptions for the Crypto MCP Server
"""


class CryptoMCPError(Exception):
    """Base exception for Crypto MCP Server"""

    pass


class ExchangeConnectionError(CryptoMCPError):
    """Raised when unable to connect to an exchange"""

    pass


class ExchangeNotSupportedError(CryptoMCPError):
    """Raised when an exchange is not supported"""

    pass


class InvalidSymbolError(CryptoMCPError):
    """Raised when a trading symbol is invalid"""

    pass


class DataFetchError(CryptoMCPError):
    """Raised when data fetching fails"""

    pass


class RateLimitError(CryptoMCPError):
    """Raised when rate limit is exceeded"""

    pass


class CacheError(CryptoMCPError):
    """Raised when cache operations fail"""

    pass


class ValidationError(CryptoMCPError):
    """Raised when input validation fails"""

    pass
