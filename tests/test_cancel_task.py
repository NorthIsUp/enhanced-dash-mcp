import asyncio
import importlib.util
from pathlib import Path
from typing import Any

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "enhanced_dash_server.py"


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


@pytest.mark.asyncio
async def test_cancel_task_finishes(stub_modules) -> None:
    """_cancel_task should finish the provided task."""
    stub_server = stub_modules["mcp.server"]
    stub_server.Server = DummyServer  # type: ignore[attr-defined]

    spec = importlib.util.spec_from_file_location("enhanced_dash_server", MODULE_PATH)
    assert spec and spec.loader
    server_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(server_mod)
    _cancel_task = server_mod._cancel_task

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
