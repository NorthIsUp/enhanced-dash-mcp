from pathlib import Path

HELP_DOC = Path(__file__).resolve().parents[1] / "docs" / "help.md"


def test_help_mentions_stdio_server():
    content = HELP_DOC.read_text()
    assert "stdio_server" in content


def test_help_mentions_initialization_options():
    content = HELP_DOC.read_text()
    assert "create_initialization_options" in content


def test_help_mentions_limit_validation():
    content = HELP_DOC.read_text()
    assert "integer `limit`" in content


def test_help_mentions_new_directories():
    content = HELP_DOC.read_text()
    assert "scripts/" in content and "configs/" in content


def test_help_mentions_dash_mcp_dir_variable():
    content = HELP_DOC.read_text()
    assert "DASH_MCP_DIR" in content


def test_help_mentions_default_directory():
    content = HELP_DOC.read_text()
    assert "enhanced-dash-mcp" in content
