# Help Guide

This project provides an MCP server that interacts with Dash docsets.

- Run the server with `python3 enhanced_dash_server.py`. The script uses
  `stdio_server` internally to expose STDIO streams. Press `Ctrl+C` to
  stop the server gracefully without seeing a stack trace. Since version
   1.2.0 the server cancels its tasks properly so startup no longer hangs
  when interrupted. Cancellation for `Ctrl+C` and task timeouts now
  share a single code path via `_cancel_task`.
- If you encounter `ModuleNotFoundError: No module named 'mcp.streams'`,
  update to version 1.1.4 or later which replaces `StdioClient` with
  `stdio_server`.
- Ensure Python 3.8+ and required dependencies from `requirements.txt` are installed.
- Lint and type-check using `flake8 .` and `mypy .`; configuration files are
  provided in `.flake8` and `mypy.ini`.
- Logs are written to `~/.cache/dash-mcp/server.log` by default. Adjust
  `DASH_MCP_LOG_LEVEL` and `DASH_MCP_LOG_FILE` environment variables to
  control logging.

For more detailed usage, see [server_usage.md](server_usage.md).
