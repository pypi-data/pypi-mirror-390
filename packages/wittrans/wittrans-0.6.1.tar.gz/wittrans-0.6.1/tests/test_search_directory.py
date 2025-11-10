from pathlib import Path
from unittest.mock import patch

import pytest

from wittrans.functions import search_directory


@pytest.fixture
def mock_progress():
    """Create a mock Progress object with the required methods."""

    class MockProgress:
        def __init__(self):
            self.tasks = {}
            self.advance_calls = 0

        def add_task(self, description, total=None):
            task_id = "task_id"
            self.tasks[task_id] = {
                "description": description,
                "total": total,
                "completed": 0,
            }
            return task_id

        def advance(self, task_id, advance=1):
            self.advance_calls += 1
            self.tasks[task_id]["completed"] += advance

    return MockProgress()


def test_search_directory_empty(monkeypatch, mock_progress):
    """Test search with empty directory."""
    # Mock find_mo_files to return an empty list
    monkeypatch.setattr("wittrans.functions.find_mo_files", lambda path: [])

    result = search_directory(Path("/test"), "search", mock_progress)

    assert result == []
    assert mock_progress.advance_calls == 0
    assert len(mock_progress.tasks) == 0  # No task created for empty directories


def test_search_directory_no_matches(monkeypatch, mock_progress):
    """Test search with files but no matches."""
    files = [Path("/test/file1.mo"), Path("/test/file2.mo")]

    # Mock dependencies - need to patch the module, not just monkeypatch
    monkeypatch.setattr("wittrans.functions.find_mo_files", lambda path: files)

    # Use patch to mock search_mo_file in the subprocess
    with patch("wittrans.functions.search_mo_file", return_value=[]):
        result = search_directory(Path("/test"), "search", mock_progress)

    assert result == []
    assert mock_progress.advance_calls == 2
    assert len(mock_progress.tasks) == 1
    assert list(mock_progress.tasks.values())[0]["total"] == 2


def test_search_directory_with_matches(monkeypatch, mock_progress):
    """Test search with matches found."""
    file1 = Path("/test/file1.mo")
    file2 = Path("/test/file2.mo")
    files = [file1, file2]

    matches1 = [("original1", "translated1", None)]
    matches2 = [("original2", "translated2", "context")]

    monkeypatch.setattr("wittrans.functions.find_mo_files", lambda path: files)

    def mock_search_mo_file(file_path, term):
        # The multiprocessing wrapper passes (file_path, search_term) as args
        if file_path == file1:
            return matches1
        elif file_path == file2:
            return matches2
        return []

    with patch("wittrans.functions.search_mo_file", side_effect=mock_search_mo_file):
        result = search_directory(Path("/test"), "search", mock_progress)

    assert len(result) == 2
    assert result[0] == (file1, matches1)
    assert result[1] == (file2, matches2)
    assert mock_progress.advance_calls == 2
    assert len(mock_progress.tasks) == 1
    assert list(mock_progress.tasks.values())[0]["total"] == 2


def test_search_directory_mixed_matches(monkeypatch, mock_progress):
    """Test search with some matches and some non-matches."""
    file1 = Path("/test/file1.mo")
    file2 = Path("/test/file2.mo")
    file3 = Path("/test/file3.mo")
    files = [file1, file2, file3]

    # Create test matches - only file1 and file3 have matches
    matches1 = [("original1", "translated1", None)]
    matches3 = [("original3", "translated3", "context")]

    # Mock dependencies
    monkeypatch.setattr("wittrans.functions.find_mo_files", lambda path: files)

    def mock_search_mo_file(file_path, term):
        if file_path == file1:
            return matches1
        elif file_path == file3:
            return matches3
        return []

    with patch("wittrans.functions.search_mo_file", side_effect=mock_search_mo_file):
        result = search_directory(Path("/test"), "search", mock_progress)

    assert len(result) == 2
    assert result[0] == (file1, matches1)
    assert result[1] == (file3, matches3)
    assert mock_progress.advance_calls == 3
    assert len(mock_progress.tasks) == 1
    assert list(mock_progress.tasks.values())[0]["total"] == 3
