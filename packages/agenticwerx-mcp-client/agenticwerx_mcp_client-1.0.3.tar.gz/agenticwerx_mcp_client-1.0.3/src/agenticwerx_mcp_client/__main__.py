#!/usr/bin/env python3
"""
AgenticWerx MCP Client - Entry point for uvx execution

This module serves as the main entry point when the package is executed
via uvx or python -m agenticwerx_mcp_client.
"""

import argparse
import asyncio
import logging
import os
import sys

from .client import AgenticWerxMCPClient


def setup_logging(debug: bool = False) -> None:
    """Configure logging for the application."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )


def get_api_key(args_api_key: str | None) -> str:
    """Get API key from arguments or environment variables."""
    api_key = args_api_key or os.getenv("AGENTICWERX_API_KEY")

    if not api_key:
        print(
            "Error: API key required via --api-key argument or AGENTICWERX_API_KEY environment variable",
            file=sys.stderr,
        )
        print(
            "Get your API key at: https://agenticwerx.com/dashboard/api-keys",
            file=sys.stderr,
        )
        sys.exit(1)

    return api_key


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="AgenticWerx MCP Client - Universal code analysis for all IDEs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with API key from environment
  export AGENTICWERX_API_KEY=your_key_here
  agenticwerx-mcp-client

  # Run with API key as argument
  agenticwerx-mcp-client --api-key your_key_here



  # Run with debug logging
  agenticwerx-mcp-client --api-key your_key_here --debug

For more information, visit: https://docs.agenticwerx.com/mcp-client
        """,
    )

    parser.add_argument(
        "--api-key",
        type=str,
        help="AgenticWerx API key (can also use AGENTICWERX_API_KEY env var)",
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    parser.add_argument(
        "--version",
        action="version",
        version=f"agenticwerx-mcp-client {__import__('agenticwerx_mcp_client').__version__}",
    )

    return parser


async def async_main() -> None:
    """Async main function."""
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)

    # Get API key
    api_key = get_api_key(args.api_key)

    logger.info("Starting AgenticWerx MCP Client...")
    logger.debug("Debug logging enabled")

    try:
        # Create and run the MCP client
        client = AgenticWerxMCPClient(api_key=api_key, debug=args.debug)

        await client.run()

    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        if args.debug:
            logger.exception("Full traceback:")
        sys.exit(1)


def main() -> None:
    """Main entry point for the application."""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
