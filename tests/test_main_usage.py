import re
from pathlib import Path

FILE_PATH = Path(__file__).resolve().parents[1] / "enhanced_dash_server.py"


def test_stdio_server_used():
    """Ensure the main section wires the server with stdio_server."""
    lines = FILE_PATH.read_text().splitlines()
    snippet = "\n".join(lines[-6:])
    assert "stdio_server" in snippet, "stdio_server not used"
    assert "server.run" in snippet, "server.run call missing"


def test_asyncio_run_invocation():
    """Ensure asyncio.run wraps main coroutine."""
    content = FILE_PATH.read_text()
    pattern = re.compile(r"asyncio\.run\(main\(\)\)")
    assert pattern.search(content), "asyncio.run invocation malformed"
