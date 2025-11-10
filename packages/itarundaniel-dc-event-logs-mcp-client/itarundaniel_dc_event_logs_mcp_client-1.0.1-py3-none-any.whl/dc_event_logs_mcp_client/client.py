#!/usr/bin/env python3
"""
MCP HTTP Client Proxy - Connects Claude Desktop to Remote HTTP MCP Server
This runs locally and acts as an stdio-to-HTTP bridge
"""

import asyncio
import sys
import logging
import os
from pathlib import Path
from mcp.client.sse import sse_client
from mcp.server.stdio import stdio_server

# Configure logging to user's home directory
log_dir = Path.home() / ".dc-event-logs-mcp-client"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "mcp_http_client.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
    ]
)
logger = logging.getLogger("mcp-http-client")

# Get MCP server URL from environment variable or use default
MCP_SERVER_URL = os.getenv("DC_EVENT_LOGS_MCP_SERVER_URL", "http://localhost:8000/sse")


async def run_proxy():
    """
    Create a bridge between stdio (Claude Desktop) and HTTP/SSE (remote server)
    Uses MCP SDK to handle all protocol details
    """
    try:
        logger.info("Starting MCP HTTP Client Proxy")
        logger.info(f"Connecting to remote server: {MCP_SERVER_URL}")

        # Connect to remote HTTP MCP server
        async with sse_client(MCP_SERVER_URL) as (remote_read, remote_write):
            logger.info("Connected to remote MCP server via SSE")

            # Set up stdio connection to Claude Desktop
            async with stdio_server() as (stdio_read, stdio_write):
                logger.info("stdio server ready for Claude Desktop")

                # Create tasks to forward messages bidirectionally
                async def forward_to_remote():
                    """Forward messages from Claude Desktop to remote server"""
                    try:
                        while True:
                            message = await stdio_read.receive()
                            logger.debug(f"Forwarding to remote: {message}")
                            await remote_write.send(message)
                    except Exception as e:
                        logger.error(f"Error forwarding to remote: {e}", exc_info=True)

                async def forward_to_stdio():
                    """Forward messages from remote server to Claude Desktop"""
                    try:
                        while True:
                            message = await remote_read.receive()
                            logger.debug(f"Forwarding to Claude: {message}")
                            await stdio_write.send(message)
                    except Exception as e:
                        logger.error(f"Error forwarding to stdio: {e}", exc_info=True)

                # Run both forwarding tasks concurrently
                logger.info("Starting bidirectional message forwarding")
                await asyncio.gather(
                    forward_to_remote(),
                    forward_to_stdio()
                )

    except Exception as e:
        logger.error(f"Fatal error in proxy: {type(e).__name__}: {str(e)}", exc_info=True)
        sys.exit(1)


def main():
    """Entry point for the package"""
    try:
        asyncio.run(run_proxy())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
