import asyncio
import importlib.util
from pathlib import Path
from typing import Any

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "enhanced_dash_server.py"


class DummyServer:
    def __init__(self, *_args: Any, **_kwargs: Any) -> None:
        pass

    def list_tools(self) -> Any:
        def decorator(func: Any) -> Any:
            return func
        return decorator

    def call_tool(self) -> Any:
        def decorator(func: Any) -> Any:
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                return await func(*args, **kwargs)
            return wrapper
        return decorator

    async def run(self, *_args: Any, **_kwargs: Any) -> None:  # pragma: no cover
        pass


@pytest.mark.asyncio
async def test_env_var_sets_docsets_path(monkeypatch, tmp_path, stub_modules) -> None:
    stub_modules["mcp.server"].Server = DummyServer  # type: ignore[attr-defined]

    docsets_root = tmp_path / "DocSets"
    resources = docsets_root / "Sample.docset" / "Contents" / "Resources"
    resources.mkdir(parents=True)
    (resources / "docSet.dsidx").write_text("")

    monkeypatch.setenv("DASH_DOCSETS_PATH", str(docsets_root))

    spec = importlib.util.spec_from_file_location("enhanced_dash_server", MODULE_PATH)
    assert spec and spec.loader
    server_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(server_mod)

    dash_server = server_mod.DashMCPServer()
    docsets = await dash_server.get_available_docsets()
    names = {d["name"] for d in docsets}
    assert "Sample" in names
