import sys
import types
from typing import Any

import pytest


@pytest.fixture
def stub_modules(monkeypatch):
    """Provide minimal MCP and third-party stubs for tests."""
    stub_mcp = types.ModuleType("mcp")
    stub_server = types.ModuleType("server")
    # Provide decorators expected by enhanced_dash_server

    def list_tools() -> Any:
        def decorator(func: Any) -> Any:
            return func
        return decorator

    def call_tool() -> Any:
        def decorator(func: Any) -> Any:
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                return await func(*args, **kwargs)

            return wrapper
        return decorator

    stub_server.list_tools = list_tools  # type: ignore[attr-defined]
    stub_server.call_tool = call_tool  # type: ignore[attr-defined]
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

    async def _stdio():  # pragma: no cover - stub
        return ""

    stub_stdio.stdio_server = _stdio  # type: ignore[attr-defined]
    stub_bs4.BeautifulSoup = object  # type: ignore[attr-defined]
    stub_fuzzywuzzy.fuzz = types.SimpleNamespace(ratio=lambda *_a, **_k: 0)  # type: ignore[attr-defined]
    stub_fuzzywuzzy.process = types.SimpleNamespace(extract=lambda *_a, **_k: [])  # type: ignore[attr-defined]
    stub_aiofiles.open = lambda *_a, **_k: None  # type: ignore[attr-defined]
    stub_aiohttp.ClientSession = object  # type: ignore[attr-defined]

    modules = {
        "mcp": stub_mcp,
        "mcp.server": stub_server,
        "mcp.server.stdio": stub_stdio,
        "mcp.types": stub_types,
        "bs4": stub_bs4,
        "fuzzywuzzy": stub_fuzzywuzzy,
        "aiofiles": stub_aiofiles,
        "aiohttp": stub_aiohttp,
    }

    for name, module in modules.items():
        monkeypatch.setitem(sys.modules, name, module)

    yield modules

    for name in modules:
        monkeypatch.delitem(sys.modules, name, raising=False)
