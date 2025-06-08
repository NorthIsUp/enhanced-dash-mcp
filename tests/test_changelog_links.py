import re
from pathlib import Path

CHANGELOG = Path(__file__).resolve().parents[1] / "CHANGELOG.md"

REPO_URL = "https://github.com/joshuadanpeterson/enhanced-dash-mcp"
# Use double braces so f-string doesn't interpret regex quantifiers
LINK_RE = re.compile(
    rf"^## \[(\d+\.\d+\.\d+)\]\({REPO_URL}/releases/tag/v\1\) - \d{{4}}-\d{{2}}-\d{{2}}$"
)


def test_changelog_version_links():
    lines = [line.strip() for line in CHANGELOG.read_text().splitlines() if line.startswith('## [')]
    assert lines, "No version headers found"
    for line in lines:
        assert LINK_RE.match(line), f"Version header not linked correctly: {line}"
