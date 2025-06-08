# Running the Enhanced Dash MCP Server

The server communicates over standard input and output. It uses the
`stdio_server` context manager from the MCP library to expose its streams
for MCP clients. An asynchronous `main` coroutine obtains these streams and
wires them to `server.run` using `asyncio.run`.

Example:

```bash
python3 enhanced_dash_server.py
```

This invocation wires the server to STDIO internally and requires no
additional parameters.

Since version 1.1.4 the main script uses `stdio_server` to obtain read and
write streams for `server.run()`. This prevents errors like:

```
TypeError: Server.run() missing 3 required positional arguments
```

Just run the script directly and the server will wire itself to STDIO.
Press `Ctrl+C` to stop the server gracefully; the program handles
`KeyboardInterrupt` without printing a stack trace. Version 1.2.7 adds startup
and shutdown log messages and fixes
an issue where the server could hang during startup when interrupted.
Both `KeyboardInterrupt` and internal cancellations use the same
`_cancel_task` helper to ensure consistent cleanup. The server now calls
`server.create_initialization_options()` before invoking `server.run()` to
avoid AttributeError warnings from MCP clients expecting structured
initialization data.

Logs are stored in `~/.cache/dash-mcp/server.log` with rotation.
Set `DASH_MCP_LOG_LEVEL` to control verbosity or `DASH_MCP_LOG_FILE`
to change the path.
Set `DASH_DOCSETS_PATH` only if your Dash documentation lives outside the default path.
Symlinks under `~/Library/Application Support/Dash` are followed automatically.
If the variable points at the `Dash` directory rather than `DocSets`, the server
will automatically correct the search path.
The log will record startup, shutdown, and unexpected error messages so you can
confirm the server launched correctly and diagnose failures.
