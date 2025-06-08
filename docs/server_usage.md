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
