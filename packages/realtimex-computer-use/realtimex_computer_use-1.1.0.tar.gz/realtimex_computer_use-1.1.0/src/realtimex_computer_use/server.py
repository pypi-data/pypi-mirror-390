"""
MCP Computer Use Server

Provides computer control tools for AI agents, including browser control
and system automation capabilities.
"""

from fastmcp import FastMCP
from .tools import browser, credentials, credential_typing


mcp = FastMCP("MCP Computer Use Server")


# Register browser control tools
mcp.tool()(browser.open_browser)
mcp.tool()(browser.open_browser_new_tab)
mcp.tool()(browser.open_browser_new_window)

# Register credential management tools
mcp.tool()(credentials.get_credentials)
mcp.tool()(credential_typing.type_credential_field)
