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
async def test_symlink_resolved(monkeypatch, tmp_path, stub_modules) -> None:
    stub_modules["mcp.server"].Server = DummyServer  # type: ignore[attr-defined]

    # create actual docsets path
    actual = tmp_path / "Dropbox" / "DocSets"
    resources = actual / "Sample.docset" / "Contents" / "Resources"
    resources.mkdir(parents=True)
    (resources / "docSet.dsidx").write_text("")

    # create default path with symlink
    library = tmp_path / "Library" / "Application Support"
    library.mkdir(parents=True)
    (library / "Dash").symlink_to(actual.parent)

    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    spec = importlib.util.spec_from_file_location("enhanced_dash_server", MODULE_PATH)
    assert spec and spec.loader
    server_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(server_mod)

    dash_server = server_mod.DashMCPServer()
    docsets = await dash_server.get_available_docsets()
    names = {d["name"] for d in docsets}
    assert "Sample" in names


@pytest.mark.asyncio
async def test_env_points_to_dash(monkeypatch, tmp_path, stub_modules) -> None:
    """DASH_DOCSETS_PATH can refer to the Dash directory and still work."""
    stub_modules["mcp.server"].Server = DummyServer  # type: ignore[attr-defined]

    dash_root = tmp_path / "Dropbox"
    resources = dash_root / "DocSets" / "Sample.docset" / "Contents" / "Resources"
    resources.mkdir(parents=True)
    (resources / "docSet.dsidx").write_text("")

    monkeypatch.setenv("DASH_DOCSETS_PATH", str(dash_root))

    spec = importlib.util.spec_from_file_location("enhanced_dash_server", MODULE_PATH)
    assert spec and spec.loader
    server_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(server_mod)

    dash_server = server_mod.DashMCPServer()
    docsets = await dash_server.get_available_docsets()
    names = {d["name"] for d in docsets}
    assert "Sample" in names


@pytest.mark.asyncio
async def test_env_symlink_to_docsets(monkeypatch, tmp_path, stub_modules) -> None:
    """DASH_DOCSETS_PATH can point to a symlink of the DocSets folder."""
    stub_modules["mcp.server"].Server = DummyServer  # type: ignore[attr-defined]

    actual = tmp_path / "Actual" / "DocSets"
    resources = actual / "Sample.docset" / "Contents" / "Resources"
    resources.mkdir(parents=True)
    (resources / "docSet.dsidx").write_text("")

    symlink = tmp_path / "LinkedDocSets"
    symlink.symlink_to(actual)

    monkeypatch.setenv("DASH_DOCSETS_PATH", str(symlink))

    spec = importlib.util.spec_from_file_location("enhanced_dash_server", MODULE_PATH)
    assert spec and spec.loader
    server_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(server_mod)

    dash_server = server_mod.DashMCPServer()
    assert dash_server.docsets_path == actual.resolve()
    docsets = await dash_server.get_available_docsets()
    names = {d["name"] for d in docsets}
    assert "Sample" in names
