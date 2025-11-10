"""
AgenticWerx MCP Client

A Model Context Protocol (MCP) client for AgenticWerx rule packages.
Provides universal code analysis across all IDEs and programming languages.
"""

__version__ = "1.0.3"
__author__ = "AgenticWerx"
__email__ = "support@agenticwerx.com"

from .api import AgenticWerxAPI
from .client import AgenticWerxMCPClient

__all__ = ["AgenticWerxMCPClient", "AgenticWerxAPI"]
