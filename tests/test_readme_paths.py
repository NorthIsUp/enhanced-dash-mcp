from pathlib import Path

README = Path(__file__).resolve().parents[1] / "README.md"


def test_readme_uses_script_paths():
    content = README.read_text()
    assert "scripts/setup-dash-mcp.sh" in content
    assert "scripts/setup-warp-dash-mcp.sh" in content
