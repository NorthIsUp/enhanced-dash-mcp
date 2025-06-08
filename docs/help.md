# Help Guide

This project provides an MCP server that interacts with Dash docsets.

- Run the server with `python3 enhanced_dash_server.py`. The script uses
  `stdio_server` internally to expose STDIO streams.
- If you encounter `ModuleNotFoundError: No module named 'mcp.streams'`,
  update to version 1.1.3 or later which replaces `StdioClient` with
  `stdio_server`.
- Ensure Python 3.8+ and required dependencies from `requirements.txt` are installed.

For more detailed usage, see [server_usage.md](server_usage.md).
