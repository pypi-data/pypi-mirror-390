from pathlib import Path

from wittrans.functions import find_mo_files


def test_find_mo_files_success(tmp_path):
    """Test finding .mo files in a directory structure."""
    # Create a test directory structure with .mo files
    mo_dir1 = tmp_path / "dir1" / "locale"
    mo_dir2 = tmp_path / "dir2" / "locale" / "en"
    mo_dir1.mkdir(parents=True)
    mo_dir2.mkdir(parents=True)

    mo_file1 = mo_dir1 / "messages.mo"
    mo_file2 = mo_dir2 / "messages.mo"
    mo_file3 = mo_dir2 / "dialog.mo"

    mo_file1.write_text("dummy content")
    mo_file2.write_text("dummy content")
    mo_file3.write_text("dummy content")

    txt_file = mo_dir1 / "readme.txt"
    txt_file.write_text("This is not a .mo file")

    result = find_mo_files(tmp_path)

    assert len(result) == 3
    assert mo_file1 in result
    assert mo_file2 in result
    assert mo_file3 in result
    assert txt_file not in result

    # Make sure all paths in result are Path objects
    assert all(isinstance(path, Path) for path in result)


def test_find_mo_files_empty_directory(tmp_path):
    """Test finding .mo files in an empty directory."""
    (tmp_path / "empty").mkdir()

    result = find_mo_files(tmp_path)

    # Should return an empty list
    assert result == []


def test_find_mo_files_permission_error(tmp_path, monkeypatch, mock_rprint):
    """Test handling of permission errors."""

    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    # Mock Path.rglob to raise PermissionError
    def mock_rglob(self, pattern):
        raise PermissionError("Permission denied")

    # Apply the monkey patch to Path.rglob
    monkeypatch.setattr(Path, "rglob", mock_rglob)

    result = find_mo_files(test_dir)

    assert result == []

    assert any("Warning: Permission denied" in msg for msg in mock_rprint)
    assert any(str(test_dir) in msg for msg in mock_rprint)


def test_find_mo_files_general_exception(tmp_path, monkeypatch, mock_rprint):
    """Test handling of general exceptions."""

    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    # Mock Path.rglob to raise a generic Exception
    def mock_rglob(self, pattern):
        raise RuntimeError("Something went wrong")

    # Apply the monkey patch to Path.rglob
    monkeypatch.setattr(Path, "rglob", mock_rglob)

    result = find_mo_files(test_dir)

    assert result == []

    assert any("Warning: Error scanning" in msg for msg in mock_rprint)
    assert any(str(test_dir) in msg for msg in mock_rprint)
    assert any("Something went wrong" in msg for msg in mock_rprint)


def test_find_mo_files_nonexistent_directory():
    """Test finding .mo files in a non-existent directory."""

    nonexistent_dir = Path("/path/that/does/not/exist")

    # Must raise FileNotFoundError
    result = find_mo_files(nonexistent_dir)
    assert result == []
