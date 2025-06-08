import re
from pathlib import Path

FILE_PATH = Path(__file__).resolve().parents[1] / "enhanced_dash_server.py"


def test_stdio_server_used():
    """Ensure the main coroutine wires the server with stdio_server."""
    content = FILE_PATH.read_text()
    assert "stdio_server" in content, "stdio_server not referenced"
    pattern = re.compile(r"server\.run\(read_stream,\s*write_stream,\s*\{\}\)")
    assert pattern.search(content), "server.run call with streams missing"


def test_asyncio_run_invocation():
    """Ensure asyncio.run wraps main coroutine."""
    content = FILE_PATH.read_text()
    pattern = re.compile(r"asyncio\.run\(main\(\)\)")
    assert pattern.search(content), "asyncio.run invocation malformed"
