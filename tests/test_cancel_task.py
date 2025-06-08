import asyncio
import importlib.util
from pathlib import Path
import sys
import types
from typing import Any

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "enhanced_dash_server.py"

# Stub minimal MCP modules so server can be imported without dependencies
stub_mcp = types.ModuleType("mcp")
stub_server = types.ModuleType("server")
stub_stdio = types.ModuleType("stdio")
stub_types = types.ModuleType("types")
stub_bs4 = types.ModuleType("bs4")
stub_fuzzywuzzy = types.ModuleType("fuzzywuzzy")
stub_aiofiles = types.ModuleType("aiofiles")
stub_aiohttp = types.ModuleType("aiohttp")


class Tool:  # pragma: no cover - stub
    pass


class TextContent:  # pragma: no cover - stub
    pass


stub_types.Tool = Tool  # type: ignore[attr-defined]
stub_types.TextContent = TextContent  # type: ignore[attr-defined]
stub_bs4.BeautifulSoup = object  # type: ignore[attr-defined]
stub_fuzzywuzzy.fuzz = types.SimpleNamespace(ratio=lambda *_a, **_k: 0)  # type: ignore[attr-defined]
stub_fuzzywuzzy.process = types.SimpleNamespace(extract=lambda *_a, **_k: [])  # type: ignore[attr-defined]
stub_aiofiles.open = lambda *_a, **_k: None  # type: ignore[attr-defined]
stub_aiohttp.ClientSession = object  # type: ignore[attr-defined]


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
sys.modules["bs4"] = stub_bs4
sys.modules["fuzzywuzzy"] = stub_fuzzywuzzy
sys.modules["aiofiles"] = stub_aiofiles
sys.modules["aiohttp"] = stub_aiohttp

spec = importlib.util.spec_from_file_location("enhanced_dash_server", MODULE_PATH)
assert spec and spec.loader
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)
_cancel_task = server._cancel_task


@pytest.mark.asyncio
async def test_cancel_task_finishes() -> None:
    nonlocal_flag = []

    async def forever():
        try:
            while True:
                await asyncio.sleep(0.1)
        finally:
            nonlocal_flag.append(True)

    task = asyncio.create_task(forever())
    await asyncio.sleep(0.1)
    await _cancel_task(task)
    assert task.done()
    assert nonlocal_flag
