import asyncio
import importlib.util
from pathlib import Path
import sys
import types
from typing import Any

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "enhanced_dash_server.py"

# Provide a minimal stub for the optional mcp dependency used by the server
stub_mcp = types.ModuleType("mcp")
stub_server = types.ModuleType("server")
stub_stdio = types.ModuleType("stdio")
stub_types = types.ModuleType("types")


class Tool:  # pragma: no cover - stub
    pass


class TextContent:  # pragma: no cover - stub
    pass


stub_types.Tool = Tool  # type: ignore[attr-defined]
stub_types.TextContent = TextContent  # type: ignore[attr-defined]


async def _stdio():  # pragma: no cover - stub
    return ""


stub_stdio.stdio_server = _stdio  # type: ignore[attr-defined]


class DummyServer:
    def __init__(self, *_args, **_kwargs) -> None:  # pragma: no cover - stub
        pass

    def list_tools(self) -> Any:  # pragma: no cover - stub
        def decorator(func: Any) -> Any:
            return func

        return decorator

    def call_tool(self) -> Any:  # pragma: no cover - stub
        def decorator(func: Any) -> Any:
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                return await func(*args, **kwargs)

            return wrapper

        return decorator

    async def run(self, *_args, **_kwargs) -> None:  # pragma: no cover - stub
        pass


stub_server.Server = DummyServer  # type: ignore[attr-defined]
stub_mcp.server = stub_server  # type: ignore[attr-defined]
stub_mcp.server.stdio = stub_stdio  # type: ignore[attr-defined]
stub_mcp.types = stub_types  # type: ignore[attr-defined]
sys.modules["mcp"] = stub_mcp
sys.modules["mcp.server"] = stub_server
sys.modules["mcp.server.stdio"] = stub_stdio
sys.modules["mcp.types"] = stub_types

spec = importlib.util.spec_from_file_location("enhanced_dash_server", MODULE_PATH)
assert spec and spec.loader
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)
main = server.main

from contextlib import asynccontextmanager


@asynccontextmanager
async def dummy_stdio_server():
    """Yield in-memory streams for testing."""
    class DummyStream:
        async def send(self, _data: bytes) -> None:  # type: ignore[empty-body]
            pass

        async def receive(self) -> bytes:
            await asyncio.sleep(0.1)
            return b""

    yield DummyStream(), DummyStream()


async def dummy_run(self, _r, _w, _o, **_kwargs):
    while True:
        await asyncio.sleep(0.1)


@pytest.mark.asyncio
async def test_main_handles_cancelled(monkeypatch) -> None:
    """Main should exit cleanly when cancelled."""
    monkeypatch.setattr(server, "stdio_server", dummy_stdio_server)
    monkeypatch.setattr(server, "server", type("dummy", (), {"run": dummy_run})())
    task = asyncio.create_task(main())
    await asyncio.sleep(0.1)
    task.cancel()
    result = await task
    assert result is None
