"""
Crypto MCP Server - Main package initialization
"""

__version__ = "1.0.0"
__author__ = "pratyush shukla"
__description__ = "MCP server for cryptocurrency market data"

from .server import CryptoMCPServer

__all__ = ["CryptoMCPServer"]
