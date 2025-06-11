from pathlib import Path

SETUP_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "setup-dash-mcp.sh"


def test_setup_script_uses_dash_mcp_dir() -> None:
    content = SETUP_SCRIPT.read_text()
    assert "DASH_MCP_DIR" in content
    assert "MCP_DIR" not in content.replace("DASH_MCP_DIR", "")


def test_setup_script_prompts_for_directory() -> None:
    """Ensure the script allows custom installation paths."""
    content = SETUP_SCRIPT.read_text()
    assert "Enter installation directory" in content
    assert "read -r -p" in content


def test_default_dir_uses_generic_path() -> None:
    """Ensure the default path ends with 'enhanced-dash-mcp'."""
    content = SETUP_SCRIPT.read_text()
    assert "enhanced-dash-mcp" in content
    assert "USERPROFILE" not in content
