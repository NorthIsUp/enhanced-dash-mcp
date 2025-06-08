from pathlib import Path

FILE_PATH = Path(__file__).resolve().parents[1] / "enhanced_dash_server.py"


def test_project_context_optional_lists() -> None:
    content = FILE_PATH.read_text()
    assert "dependencies: Optional[List[str]] = None" in content
    assert "current_files: Optional[List[str]] = None" in content
