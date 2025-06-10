# Help Guide

This project provides an MCP server that interacts with Dash docsets.

- Run the server with `python3 enhanced_dash_server.py`. The script uses
  `stdio_server` internally to expose STDIO streams. Press `Ctrl+C` to
  stop the server gracefully without seeing a stack trace. Since version
  1.2.11 the server logs startup, shutdown, and unexpected error events, and cancels its tasks properly so startup no longer hangs
  when interrupted. Cancellation for `Ctrl+C` and task timeouts now
  share a single code path via `_cancel_task`.
- Initialization options are now generated with
  `server.create_initialization_options()` before running the server to avoid
  `AttributeError: 'dict' object has no attribute 'capabilities'` in certain MCP
  clients.
- If you encounter `ModuleNotFoundError: No module named 'mcp.streams'`,
  update to version 1.1.4 or later which replaces `StdioClient` with
  `stdio_server`.
- Ensure Python 3.8+ and required dependencies from `requirements.txt` are installed.
- Lint and type-check using `flake8 .` and `mypy .`; configuration files are
  provided in `.flake8` and `mypy.ini`.
- When calling `search_dash_docs`, pass an integer `limit` between 1 and 100.
  Float values are cast to an integer automatically. Non-numeric values raise `ValueError`. Negative numbers are clamped to `1`.
- Logs are written to `~/.cache/dash-mcp/server.log` by default. Adjust
  `DASH_MCP_LOG_LEVEL` and `DASH_MCP_LOG_FILE` environment variables to
  control logging.
- Set `DASH_DOCSETS_PATH` only if your Dash docsets aren't under
  `~/Library/Application Support/Dash/DocSets/`.
- Symlinks to that directory are resolved automatically.
- When creating a symlink, target the parent `Dash` directory rather than the
  `DocSets` folder itself. Linking directly to `DocSets` results in a search
  path like `.../DocSets/DocSets` and the server won't find your docsets.
- The server now adjusts automatically if `DASH_DOCSETS_PATH` points to the
  `Dash` directory instead of `DocSets`.
- Docsets inside subfolders are discovered automatically so Dash 4 layouts work
  without extra configuration.
- The log file now includes startup and shutdown messages and records any unexpected errors.

- Review [CHANGELOG.md](../CHANGELOG.md) for a summary of recent releases. The changelog lists versions in reverse chronological order so the latest updates appear first and the entire history is retained for reference.

For more detailed usage, see [server_usage.md](server_usage.md).
- The changelog is automatically updated by GitHub Actions. The workflow now fetches full history so older entries stay intact.
- Shell scripts now live under `scripts/` and configuration templates under `configs/`.
- See [AGENTS.md](../AGENTS.md) and [AI_Docs/AGENTS.md](../AI_Docs/AGENTS.md) for guidelines on working with this repository using AI tools.
