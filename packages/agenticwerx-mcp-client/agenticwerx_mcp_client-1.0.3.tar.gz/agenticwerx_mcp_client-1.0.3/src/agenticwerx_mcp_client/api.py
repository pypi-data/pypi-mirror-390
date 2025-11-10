"""
AgenticWerx API client - Lambda MCP communication

This module handles communication with the AgenticWerx Lambda MCP server
using proper JSON-RPC 2.0 protocol.
"""

import logging
import random
import string
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class AgenticWerxAPIError(Exception):
    """Custom exception for API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class AgenticWerxAPI:
    """
    AgenticWerx Lambda MCP API client.

    This client connects to the AgenticWerx Lambda MCP server using
    proper JSON-RPC 2.0 protocol for MCP communication.
    """

    def __init__(self, api_key: str):
        """
        Initialize the API client.

        Args:
            api_key: AgenticWerx API key
        """
        self.api_key = api_key
        self.lambda_url = (
            "https://rph7c2jq5zpisbenj73y2hpjfm0gtwdw.lambda-url.us-west-2.on.aws/"
        )

        # Create HTTP client with proper headers and timeout
        # Note: SSL verification disabled since this connects to your own trusted Lambda endpoint
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "AgenticWerx-Lambda-MCP-Client/1.0.0",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(30.0, connect=10.0),
            verify=False,  # Safe to disable for your own Lambda endpoint
        )

        logger.debug(f"Initialized Lambda MCP client for: {self.lambda_url}")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    def _generate_request_id(self) -> str:
        """Generate a random request ID."""
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=7))

    async def _make_mcp_request(
        self, method: str, params: dict[str, Any] | None = None
    ) -> Any:
        """
        Make an MCP request to the Lambda function.

        Args:
            method: MCP method name
            params: Optional parameters for the method

        Returns:
            The result from the MCP server
        """
        request_id = self._generate_request_id()

        mcp_request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {},
        }

        logger.debug(f"Making MCP request to Lambda: {method}")
        logger.debug(f"Request payload: {mcp_request}")

        try:
            response = await self.client.post(self.lambda_url, json=mcp_request)

            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")

            if response.status_code >= 400:
                error_text = response.text
                logger.error(
                    f"Lambda function returned error: {response.status_code} {error_text}"
                )
                raise AgenticWerxAPIError(
                    f"Lambda request failed: {response.status_code}",
                    status_code=response.status_code,
                )

            try:
                result = response.json()
                logger.debug(
                    f"Lambda response received for request {request_id}: {result}"
                )
            except Exception as json_error:
                logger.error(f"Failed to parse JSON response: {json_error}")
                logger.error(f"Raw response: {response.text}")
                raise AgenticWerxAPIError(
                    f"Invalid JSON response from Lambda: {json_error}"
                ) from json_error

            if "error" in result:
                error_msg = result["error"].get("message", "Unknown MCP error")
                logger.error(f"MCP error from Lambda: {error_msg}")
                raise AgenticWerxAPIError(f"MCP Error: {error_msg}")

            return result.get("result")

        except httpx.TimeoutException as e:
            raise AgenticWerxAPIError("Request timeout") from e
        except httpx.ConnectError as e:
            raise AgenticWerxAPIError("Connection error") from e
        except Exception as e:
            logger.error(f"Error making MCP request: {e}")
            raise AgenticWerxAPIError(f"Failed to make MCP request: {str(e)}") from e

    async def test_connection(self) -> bool:
        """
        Test connection to the Lambda MCP server.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            logger.info("Testing Lambda connection...")
            result = await self._make_mcp_request("health")
            logger.info(f"Lambda connection successful: {result}")
            return True
        except Exception as e:
            logger.error(f"Lambda connection test failed: {e}")
            return False

    async def list_tools(self) -> list[dict[str, Any]]:
        """
        List available tools from the MCP server.

        Returns:
            List of available tools
        """
        try:
            result = await self._make_mcp_request("tools/list")
            return result.get("tools", [])
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return []

    async def call_tool(
        self, name: str, arguments: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Call a tool on the MCP server.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        try:
            result = await self._make_mcp_request(
                "tools/call", {"name": name, "arguments": arguments or {}}
            )
            return result
        except Exception as e:
            logger.error(f"Tool call failed for {name}: {e}")
            raise

    async def get_rules(self, package_id: str | None = None) -> dict[str, Any]:
        """
        Get rules from the AgenticWerx MCP server.

        Args:
            package_id: Optional specific package ID to retrieve

        Returns:
            Rules data from the server
        """
        logger.debug("Fetching rules via MCP tool call")

        try:
            # Use the get_rules tool via MCP
            arguments = {}
            if package_id:
                arguments["packageId"] = package_id

            result = await self.call_tool("get_rules", arguments)

            # Extract the actual rules data from the MCP response
            if "content" in result and result["content"]:
                # The content should be a list with text content
                # Look for the JSON content (usually the second item)
                json_content = None
                for content_item in result["content"]:
                    if content_item.get("type") == "text":
                        text = content_item["text"]
                        # Try to parse as JSON - if it starts with { or [, it's likely JSON
                        if text.strip().startswith(("{", "[")):
                            try:
                                import json

                                json_content = json.loads(text)
                                break
                            except json.JSONDecodeError:
                                continue

                if json_content:
                    logger.info("Successfully retrieved rules via MCP")
                    return json_content
                else:
                    # If no JSON found, return the raw content
                    logger.info("No JSON content found, returning raw content")
                    return {
                        "content": result["content"],
                        "message": "Rules retrieved but not in JSON format",
                    }

            logger.warning("No rules content found in MCP response")
            return {"rules": [], "message": "No rules found"}

        except Exception as e:
            logger.error(f"Error fetching rules via MCP: {e}")
            raise AgenticWerxAPIError(f"Failed to fetch rules: {str(e)}") from e

    async def analyze_code(
        self,
        code: str,
        language: str | None = None,
        package_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Analyze code using AgenticWerx rules.

        Args:
            code: Code to analyze
            language: Programming language (optional, will be auto-detected)
            package_ids: List of package IDs to use for analysis (optional)

        Returns:
            Analysis results from the server
        """
        logger.debug("Analyzing code via MCP tool call")

        try:
            # Use the analyze_code tool via MCP
            arguments = {"code": code}
            if language:
                arguments["language"] = language
            if package_ids:
                arguments["packageIds"] = package_ids

            result = await self.call_tool("analyze_code", arguments)

            # Extract the actual analysis data from the MCP response
            if "content" in result and result["content"]:
                # The content should be a list with text content
                json_content = None
                for content_item in result["content"]:
                    if content_item.get("type") == "text":
                        text = content_item["text"]
                        # Try to parse as JSON
                        if text.strip().startswith(("{", "[")):
                            try:
                                import json

                                json_content = json.loads(text)
                                break
                            except json.JSONDecodeError:
                                continue

                if json_content:
                    logger.info("Successfully analyzed code via MCP")
                    return json_content
                else:
                    # If no JSON found, return the raw content
                    logger.info("No JSON content found, returning raw content")
                    return {
                        "content": result["content"],
                        "message": "Analysis completed but not in JSON format",
                    }

            logger.warning("No analysis content found in MCP response")
            return {"issues": [], "message": "No analysis results found"}

        except Exception as e:
            logger.error(f"Error analyzing code via MCP: {e}")
            raise AgenticWerxAPIError(f"Failed to analyze code: {str(e)}") from e
