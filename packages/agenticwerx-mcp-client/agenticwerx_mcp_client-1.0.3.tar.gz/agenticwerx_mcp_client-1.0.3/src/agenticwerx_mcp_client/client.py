"""
AgenticWerx MCP Client - Simple rule retrieval client

This module implements a simple MCP server that connects to your
AgenticWerx MCP server to retrieve rules.
"""

import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Resource, TextContent, Tool

from .api import AgenticWerxAPI, AgenticWerxAPIError

logger = logging.getLogger(__name__)


class AgenticWerxMCPClient:
    """
    Simple AgenticWerx MCP Client for rule retrieval.

    This client connects to your AgenticWerx MCP server and provides
    a simple interface to get rules through the MCP protocol.
    """

    def __init__(self, api_key: str, debug: bool = False):
        """
        Initialize the MCP client.

        Args:
            api_key: AgenticWerx API key
            debug: Enable debug logging
        """
        self.api_key = api_key
        self.debug = debug

        # Initialize the API client
        self.api = AgenticWerxAPI(api_key)

        # Initialize the MCP server
        self.server = Server("agenticwerx")

        # Configure logging
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)

        logger.info("Initializing AgenticWerx MCP Client")

        # Set up MCP handlers
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up MCP server handlers."""

        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """List available rule resources."""
            logger.debug("Listing available rule resources")

            try:
                # Test if we can get rules from the Lambda MCP server
                await self.api.get_rules()

                # Create a single resource for all rules
                resource = Resource(
                    uri="agenticwerx://rules",
                    name="AgenticWerx Rules",
                    description="All available AgenticWerx rules from Lambda MCP server",
                    mimeType="application/json",
                )

                logger.info("Listed rule resources from Lambda MCP server")
                return [resource]

            except AgenticWerxAPIError as e:
                logger.error(f"API error listing resources: {e}")
                return []
            except Exception as e:
                logger.error(f"Unexpected error listing resources: {e}")
                return []

        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read rule resource."""
            logger.debug(f"Reading resource: {uri}")

            if uri != "agenticwerx://rules":
                raise ValueError(f"Unknown resource URI: {uri}")

            try:
                rules_data = await self.api.get_rules()
                logger.debug("Successfully read rules resource from Lambda MCP server")
                return json.dumps(rules_data, indent=2)

            except AgenticWerxAPIError as e:
                logger.error(f"API error reading resource: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error reading resource: {e}")
                raise ValueError(f"Failed to read resource: {str(e)}") from e

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            logger.debug("Listing available tools")

            # Provide get_rules and analyze_code tools
            tools = [
                Tool(
                    name="get_rules",
                    description="Get AgenticWerx rules. Optionally specify a packageId to use rules from a specific package.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "packageId": {
                                "type": "string",
                                "description": "Optional package ID to use rules from a specific package",
                            }
                        },
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="analyze_code",
                    description="Analyze code using AgenticWerx rules. Provide code snippet, optional language, and optional package IDs.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Code to analyze",
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language (optional, will be auto-detected)",
                            },
                            "packageIds": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of package IDs to use for analysis (optional)",
                            },
                        },
                        "required": ["code"],
                        "additionalProperties": False,
                    },
                ),
            ]

            logger.info(f"Listed {len(tools)} available tools")
            return tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Execute a tool."""
            logger.debug(f"Executing tool: {name}")

            try:
                if name == "get_rules":
                    # Handle get_rules tool
                    package_id = arguments.get("packageId") or arguments.get(
                        "package_id"
                    )
                    result = await self.api.get_rules(package_id)

                    response = {
                        "tool": "get_rules",
                        "packageId": package_id,
                        "rules": result,
                    }

                    logger.debug("Successfully retrieved rules")
                    return [
                        TextContent(type="text", text=json.dumps(response, indent=2))
                    ]

                elif name == "analyze_code":
                    # Handle analyze_code tool
                    code = arguments.get("code")
                    if not code:
                        error_msg = "Missing required parameter: code"
                        logger.warning(error_msg)
                        return [
                            TextContent(
                                type="text",
                                text=json.dumps({"error": error_msg}, indent=2),
                            )
                        ]

                    language = arguments.get("language")
                    package_ids = arguments.get("packageIds") or arguments.get(
                        "package_ids"
                    )

                    result = await self.api.analyze_code(code, language, package_ids)

                    response = {
                        "tool": "analyze_code",
                        "language": language,
                        "packageIds": package_ids,
                        "analysis": result,
                    }

                    logger.debug("Successfully analyzed code")
                    return [
                        TextContent(type="text", text=json.dumps(response, indent=2))
                    ]

                else:
                    # Unsupported tool
                    error_msg = f"Tool '{name}' is not supported. Available tools: get_rules, analyze_code"
                    logger.warning(f"Unsupported tool requested: {name}")
                    return [
                        TextContent(
                            type="text", text=json.dumps({"error": error_msg}, indent=2)
                        )
                    ]

            except AgenticWerxAPIError as e:
                error_msg = f"AgenticWerx API Error: {str(e)}"
                logger.error(f"API error in tool {name}: {e}")
                return [
                    TextContent(
                        type="text", text=json.dumps({"error": error_msg}, indent=2)
                    )
                ]

            except Exception as e:
                error_msg = f"Tool execution error: {str(e)}"
                logger.error(f"Unexpected error in tool {name}: {e}")
                return [
                    TextContent(
                        type="text", text=json.dumps({"error": error_msg}, indent=2)
                    )
                ]

    async def test_connection(self) -> bool:
        """Test connection to the Lambda MCP server."""
        return await self.api.test_connection()

    async def run(self) -> None:
        """Run the MCP server."""
        logger.info("Starting AgenticWerx MCP Client")

        # Test connection to Lambda MCP server on startup
        logger.info("Testing connection to Lambda MCP server...")
        connection_ok = await self.test_connection()
        if not connection_ok:
            logger.error("Failed to connect to Lambda MCP server")
            # Continue anyway - the client might still work for some operations
        else:
            logger.info("Successfully connected to Lambda MCP server")

        try:
            from mcp.server.stdio import stdio_server

            async with stdio_server() as (read_stream, write_stream):
                logger.info("MCP Client started, waiting for connections...")

                from mcp.types import (
                    ResourcesCapability,
                    ServerCapabilities,
                    ToolsCapability,
                )

                init_options = InitializationOptions(
                    server_name="agenticwerx",
                    server_version="1.0.0",
                    capabilities=ServerCapabilities(
                        resources=ResourcesCapability(
                            subscribe=False, listChanged=False
                        ),
                        tools=ToolsCapability(listChanged=False),
                    ),
                )

                await self.server.run(read_stream, write_stream, init_options)

        except Exception as e:
            logger.error(f"Error running MCP server: {e}")
            raise
        finally:
            await self.api.close()
            logger.info("AgenticWerx MCP Client stopped")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.api.close()
