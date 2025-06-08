import re
from pathlib import Path

FILE_PATH = Path(__file__).resolve().parents[1] / "enhanced_dash_server.py"


def test_async_stdio_server_used():
    """Ensure the async main coroutine wires `server.run` with stdio_server."""
    content = FILE_PATH.read_text()
    assert "stdio_server" in content, "stdio_server not referenced"
    assert "server.create_initialization_options()" in content
    pattern = re.compile(
        r"server\.run\(\s*read_stream\s*,\s*write_stream\s*,\s*init_options\s*\)"
    )
    assert pattern.search(content), "server.run call with init_options missing"


def test_asyncio_run_invocation():
    """Ensure asyncio.run wraps main coroutine."""
    content = FILE_PATH.read_text()
    pattern = re.compile(r"asyncio\.run\(main\(\)\)")
    assert pattern.search(content), "asyncio.run invocation malformed"
