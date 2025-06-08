import importlib.util
import logging
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "enhanced_dash_server.py"


def test_configure_logging_creates_file(tmp_path, stub_modules):
    class DummyServer:
        def __init__(self, *_args, **_kwargs) -> None:  # pragma: no cover - stub
            pass

        def list_tools(self):  # pragma: no cover - stub
            def decorator(func):
                return func

            return decorator

        def call_tool(self):  # pragma: no cover - stub
            def decorator(func):
                async def wrapper(*args, **kwargs):
                    return await func(*args, **kwargs)

                return wrapper

            return decorator

    stub_modules["mcp.server"].Server = DummyServer  # type: ignore[attr-defined]
    spec = importlib.util.spec_from_file_location("enhanced_dash_server", MODULE_PATH)
    assert spec and spec.loader
    server_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(server_mod)

    log_file = tmp_path / "server.log"
    server_mod.configure_logging(logging.INFO, str(log_file))
    server_mod.logger.info("hello")
    logging.shutdown()
    assert log_file.exists()
    assert "hello" in log_file.read_text()
