# realtimex-computer-use

A MCP (Model Context Protocol) server that provides computer control tools for AI agents, enabling browser automation and system interactions.

## Features

* Open URLs in web browsers
* Support for multiple browsers (Chrome, Firefox, Safari, Edge)
* Open URLs in new tabs or windows
* Retrieve configured credentials for authentication
* Graceful fallback to system default browser
* Cross-platform support (Windows, macOS, Linux)

## Tools

The server implements the following tools:

### Browser Control

* **open_browser** - Open a URL in the specified browser or system default
* **open_browser_new_tab** - Open a URL in a new browser tab
* **open_browser_new_window** - Open a URL in a new browser window

Each tool supports browser selection (chrome, firefox, safari, edge, default) and provides graceful fallback to the system default browser if the specified browser is unavailable.

### Credential Management

* **get_credentials** - Get available credentials for authentication

Returns credential names and types for the agent to ask which credential to use for login. Configured via `CREDENTIAL_SERVER_URL` environment variable.

## Installation

### Prerequisites

* Python 3.10+
* FastMCP framework
* uv package manager

### Install Steps

Install the package:

```bash
pip install realtimex-computer-use
```

Or using uvx for immediate use:

```bash
uvx realtimex-computer-use
```

### MCP Client Configuration

To use this server with an MCP-compatible client, configure it to run the server via stdio transport.

**Development Configuration** (local installation):
```json
{
  "mcpServers": {
    "realtimex-computer-use": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/realtimex-computer-use",
        "run",
        "realtimex-computer-use"
      ]
    }
  }
}
```

**Production Configuration** (published package):
```json
{
  "mcpServers": {
    "realtimex-computer-use": {
      "command": "uvx",
      "args": [
        "realtimex-computer-use"
      ]
    }
  }
}
```

## Development

### Building and Publishing

1. Sync dependencies and update lockfile:
```bash
uv sync
```

2. Build package distributions:
```bash
uv build
```

3. Publish to PyPI:
```bash
uv publish
```

Note: Set PyPI credentials via environment variables or command flags:
* Token: `--token` or `UV_PUBLISH_TOKEN`
* Username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`

### Debugging

For the best debugging experience, use the MCP Inspector.

Launch the MCP Inspector via npm:

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/realtimex-computer-use run realtimex-computer-use
```

The Inspector will display a URL that you can access in your browser to begin debugging.

## Usage Examples

### Open a URL in the default browser
```json
{
  "tool": "open_browser",
  "arguments": {
    "url": "https://www.python.org"
  }
}
```

### Open a URL in Chrome
```json
{
  "tool": "open_browser",
  "arguments": {
    "url": "https://www.python.org",
    "browser": "chrome"
  }
}
```

### Open a URL in a new tab
```json
{
  "tool": "open_browser_new_tab",
  "arguments": {
    "url": "https://docs.python.org",
    "browser": "firefox"
  }
}
```

### Get available credentials
```json
{
  "tool": "get_credentials",
  "arguments": {}
}
```

**Configuration:** Set `CREDENTIAL_SERVER_URL` environment variable (defaults to `http://localhost:3001`)

## Future Expansion

This package is designed to support additional computer control capabilities:
* Desktop automation (PyAutoGUI integration)
* File system operations
* System information retrieval
* Process management
* Additional credential operations (select, validate)

## Architecture

The codebase is organized for maintainability and extensibility:

```
realtimex-computer-use/
├── fastmcp.json          # FastMCP configuration (dependencies)
├── pyproject.toml        # Package configuration and metadata
├── smithery.yaml         # Smithery MCP registry configuration
└── src/
    └── realtimex_computer_use/
        ├── __init__.py   # Package entry point
        ├── __main__.py   # CLI entry point
        ├── server.py        # MCP server initialization and tool registration
        └── tools/           # Modular tool implementations
            ├── __init__.py
            ├── browser.py     # Browser control tools
            └── credentials.py # Credential management tools
```

**Configuration Files:**
- `fastmcp.json`: Defines FastMCP dependencies and entrypoint (follows FastMCP 2.11.4+ standard)
- `pyproject.toml`: Python package metadata, dependencies, and build configuration
- `smithery.yaml`: Configuration for Smithery MCP server registry

**Adding New Tools:**
1. Create a new module in `src/realtimex_computer_use/tools/` (e.g., `credentials.py`)
2. Implement tool functions with proper type hints and docstrings
3. Register tools in `server.py` using `mcp.tool()(module.function_name)`

## License

This project is proprietary software. All rights reserved.