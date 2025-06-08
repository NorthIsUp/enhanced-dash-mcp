# Running the Enhanced Dash MCP Server

The server communicates over standard input and output. It uses the
`stdio_server` context manager from the MCP library to expose its streams
for MCP clients.
correctly.

Example:

```bash
python3 enhanced_dash_server.py
```

This invocation wires the server to STDIO internally and requires no
additional parameters.

Since version 1.1.2 the main script uses `stdio_server` to obtain read and
write streams for `server.run()`. This prevents errors like:

```
TypeError: Server.run() missing 3 required positional arguments
```

Just run the script directly and the server will wire itself to STDIO.
