import asyncio
import importlib.util
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "enhanced_dash_server.py"


class DummyServer:
    def __init__(self, *_args, **_kwargs) -> None:  # pragma: no cover - stub
        pass

    async def run(self, *_args, **_kwargs) -> None:  # pragma: no cover - stub
        while True:
            await asyncio.sleep(0.1)


@asynccontextmanager
def dummy_stdio_server():  # pragma: no cover - stub
    class DummyStream:
        async def send(self, _data: bytes) -> None:  # type: ignore[empty-body]
            pass

        async def receive(self) -> bytes:
            await asyncio.sleep(0.1)
            return b""

    yield DummyStream(), DummyStream()


@pytest.mark.asyncio
async def test_main_handles_cancelled(monkeypatch, stub_modules) -> None:
    """Main should exit cleanly when cancelled."""
    stub_server = stub_modules["mcp.server"]
    stub_server.Server = DummyServer  # type: ignore[attr-defined]

    spec = importlib.util.spec_from_file_location("enhanced_dash_server", MODULE_PATH)
    assert spec and spec.loader
    srv_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(srv_mod)
    main = srv_mod.main

    monkeypatch.setattr(srv_mod, "stdio_server", dummy_stdio_server)
    monkeypatch.setattr(srv_mod, "server", type("dummy", (), {"run": DummyServer().run})())

    task = asyncio.create_task(main())
    await asyncio.sleep(0.1)
    task.cancel()
    result = await task
    assert result is None


@pytest.mark.asyncio
async def test_main_handles_keyboard_interrupt(monkeypatch, stub_modules) -> None:
    """Main should return cleanly when server.run raises KeyboardInterrupt."""
    spec = importlib.util.spec_from_file_location("enhanced_dash_server", MODULE_PATH)
    assert spec and spec.loader
    srv_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(srv_mod)
    main = srv_mod.main

    async def raise_interrupt(_r, _w, _o, **_kwargs) -> None:
        raise KeyboardInterrupt

    monkeypatch.setattr(srv_mod, "stdio_server", dummy_stdio_server)
    monkeypatch.setattr(srv_mod, "server", type("dummy", (), {"run": raise_interrupt})())

    result = await main()
    assert result is None
