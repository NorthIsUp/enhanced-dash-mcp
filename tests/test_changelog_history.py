from pathlib import Path

CHANGELOG = Path(__file__).resolve().parents[1] / "CHANGELOG.md"


def test_changelog_preserves_history():
    content = CHANGELOG.read_text()
    assert "1.2.9" in content, "Previous changelog entries missing"
