import re
from datetime import datetime
from pathlib import Path

CHANGELOG = Path(__file__).resolve().parents[1] / "CHANGELOG.md"
HEADER_RE = re.compile(r"^## \[(\d+\.\d+\.\d+)\].* - (\d{4}-\d{2}-\d{2})$")


def test_changelog_in_reverse_chronological_order():
    dates = []
    for line in CHANGELOG.read_text().splitlines():
        match = HEADER_RE.match(line.strip())
        if match:
            dates.append(datetime.fromisoformat(match.group(2)))
    assert dates == sorted(dates, reverse=True), "Changelog entries not in reverse chronological order"
