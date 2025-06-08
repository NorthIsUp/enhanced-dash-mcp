from pathlib import Path

HELP_DOC = Path(__file__).resolve().parents[1] / "docs" / "help.md"


def test_help_mentions_stdio_server():
    content = HELP_DOC.read_text()
    assert "stdio_server" in content


def test_help_mentions_initialization_options():
    content = HELP_DOC.read_text()
    assert "create_initialization_options" in content
