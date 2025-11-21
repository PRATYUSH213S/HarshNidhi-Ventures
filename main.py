"""
Main entry point for the Crypto MCP Server
"""

import asyncio
from crypto_mcp_server.server import main

if __name__ == "__main__":
    asyncio.run(main())
