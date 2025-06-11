from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs" / "claude-mcp-config.json"


def test_claude_config_uses_venv_python() -> None:
    content = CONFIG_PATH.read_text()
    assert "venv/bin/python3" in content
