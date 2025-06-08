import importlib.util
import pytest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "enhanced_dash_server.py"


class DummyServer:
    def __init__(self, *_args, **_kwargs) -> None:
        pass

    def list_tools(self):
        def decorator(func):
            return func
        return decorator

    def call_tool(self):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            return wrapper
        return decorator

    async def run(self, *_args, **_kwargs):  # pragma: no cover - stub
        pass


@pytest.mark.asyncio
async def test_search_limit_casts_to_int(monkeypatch, stub_modules):
    stub_modules["mcp.server"].Server = DummyServer  # type: ignore[attr-defined]
    spec = importlib.util.spec_from_file_location("enhanced_dash_server", MODULE_PATH)
    assert spec and spec.loader
    server_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(server_mod)

    captured = {}

    async def fake_search_docset(*, query, docset_name=None, limit=20, include_content=False, use_fuzzy=True):
        captured['limit'] = limit
        return []

    monkeypatch.setattr(server_mod.dash_server, "search_docset", fake_search_docset)

    await server_mod.call_tool("search_dash_docs", {"query": "pip", "limit": 5.0})
    assert isinstance(captured['limit'], int)
