# Running the Enhanced Dash MCP Server

The server communicates over standard input and output. Ensure you run the
script using the provided `StdioClient` so that MCP clients can connect
correctly.

Example:

```bash
python3 enhanced_dash_server.py
```

This invocation wires the server to STDIO internally and requires no
additional parameters.

Since version 1.1.1 the main script automatically creates a `StdioClient` and
passes its streams to `server.run()`. This prevents errors like:

```
TypeError: Server.run() missing 3 required positional arguments
```

Just run the script directly and the server will wire itself to STDIO.
