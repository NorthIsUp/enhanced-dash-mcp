import re
from pathlib import Path

FILE_PATH = Path(__file__).resolve().parents[1] / "enhanced_dash_server.py"


def test_stdio_client_used():
    """Ensure the main section wires the server with StdioClient."""
    lines = FILE_PATH.read_text().splitlines()
    snippet = "\n".join(lines[-5:])
    assert "StdioClient" in snippet, "StdioClient not used"
    assert "server.run" in snippet, "server.run call missing"
    assert "client.read_stream" in snippet, "read stream not passed"
    assert "client.write_stream" in snippet, "write stream not passed"

