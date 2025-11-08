"""
Goodday MCP Server package.

This package provides a Model Context Protocol server for interacting with
the Goodday project management platform API.
"""

from .main import mcp
from .main import make_goodday_request
from .main import format_task, format_project, format_user

# Version
__version__ = "1.0.1"

# Export all tools
__all__ = ["mcp", "make_goodday_request", "format_task", "format_project", "format_user"]