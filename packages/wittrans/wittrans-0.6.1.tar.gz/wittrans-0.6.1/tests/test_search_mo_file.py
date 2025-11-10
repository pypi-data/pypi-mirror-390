from pathlib import Path

from wittrans.functions import search_mo_file


# Mock POEntry class to simulate polib entries
class MockPOEntry:
    def __init__(self, msgid, msgstr, msgctxt=None):
        self.msgid = msgid
        self.msgstr = msgstr
        self.msgctxt = msgctxt


# Mock MO file class to simulate polib.mofile return value
class MockMOFile(list):
    def __init__(self, entries):
        super().__init__(entries)


def test_search_mo_file_with_matches(monkeypatch):
    """Test searching a .mo file with matches in both msgid and msgstr."""
    entries = [
        MockPOEntry("Hello", "Hei", "greeting"),
        MockPOEntry("Goodbye", "Näkemiin", "farewell"),
        MockPOEntry("Welcome", "Tervetuloa", None),
        MockPOEntry("Thanks", "Kiitos", "gratitude"),
    ]

    # Mock polib.mofile to return our mock entries
    def mock_mofile(file_path, encoding):
        return MockMOFile(entries)

    monkeypatch.setattr("polib.mofile", mock_mofile)

    # Test with a search term in msgid
    result1 = search_mo_file(Path("/test/file.mo"), "Hello")
    assert len(result1) == 1
    assert result1[0] == ("Hello", "Hei", "greeting")

    # Test with a search term in msgstr
    result2 = search_mo_file(Path("/test/file.mo"), "terve")
    assert len(result2) == 1
    assert result2[0] == ("Welcome", "Tervetuloa", None)

    # Test with a search term that matches multiple entries (case insensitive)
    result3 = search_mo_file(Path("/test/file.mo"), "e")
    assert len(result3) == 3  # Should match Hello, Welcome, Tervetuloa
    assert ("Hello", "Hei", "greeting") in result3
    assert ("Welcome", "Tervetuloa", None) in result3
    assert ("Goodbye", "Näkemiin", "farewell") in result3


def test_search_mo_file_no_matches(monkeypatch):
    """Test searching a .mo file with no matches."""
    # Create mock entries
    entries = [
        MockPOEntry("Hello", "Hei", "greeting"),
        MockPOEntry("Goodbye", "Näkemiin", "farewell"),
    ]

    # Mock polib.mofile to return our mock entries
    def mock_mofile(file_path, encoding):
        return MockMOFile(entries)

    monkeypatch.setattr("polib.mofile", mock_mofile)

    # Test with a search term that doesn't match anything
    result = search_mo_file(Path("/test/file.mo"), "xyz")
    assert result == []


def test_search_mo_file_empty(monkeypatch):
    """Test searching an empty .mo file."""

    # Mock polib.mofile to return empty list
    def mock_mofile(file_path, encoding):
        return MockMOFile([])

    monkeypatch.setattr("polib.mofile", mock_mofile)

    # Test with any search term
    result = search_mo_file(Path("/test/file.mo"), "test")
    assert result == []


def test_search_mo_file_error(monkeypatch, mock_rprint):
    """Test error handling when processing a .mo file fails."""

    # Mock polib.mofile to raise an exception
    def mock_mofile(file_path, encoding):
        raise ValueError("Invalid file format")

    monkeypatch.setattr("polib.mofile", mock_mofile)

    # Test with any search term
    result = search_mo_file(Path("/test/file.mo"), "hei")

    # Verify the result is empty
    assert result == []

    # Verify error message was printed
    assert len(mock_rprint) == 1
    assert "[red]Error processing file" in mock_rprint[0]
    assert "Invalid file format" in mock_rprint[0]


def test_search_mo_file_case_insensitive(monkeypatch):
    """Test that search is case insensitive."""
    entries = [
        MockPOEntry("Hello", "Hei", "greeting"),
        MockPOEntry("WELCOME", "TERVETULOA", None),
    ]

    # Mock polib.mofile to return our mock entries
    def mock_mofile(file_path, encoding):
        return MockMOFile(entries)

    monkeypatch.setattr("polib.mofile", mock_mofile)

    # Test with lowercase search terms
    result1 = search_mo_file(Path("/test/file.mo"), "hello")
    assert len(result1) == 1
    assert result1[0] == ("Hello", "Hei", "greeting")

    # Test with uppercase search terms
    result2 = search_mo_file(Path("/test/file.mo"), "TERVETU")
    assert len(result2) == 1
    assert result2[0] == ("WELCOME", "TERVETULOA", None)

    # Test with mixed case search terms
    result3 = search_mo_file(Path("/test/file.mo"), "WeLcOme")
    assert len(result3) == 1
    assert result3[0] == ("WELCOME", "TERVETULOA", None)


def test_search_mo_file_finnish_special_chars(monkeypatch):
    """Test searching with Finnish special characters (ä, ö)."""
    entries = [
        MockPOEntry("Settings", "Asetukset", None),
        MockPOEntry("User", "Käyttäjä", None),
        MockPOEntry("Friends", "Ystävät", None),
        MockPOEntry("Summer", "Kesä", None),
        MockPOEntry("Night", "Yö", None),
    ]

    # Mock polib.mofile to return our mock entries
    def mock_mofile(file_path, encoding):
        return MockMOFile(entries)

    monkeypatch.setattr("polib.mofile", mock_mofile)

    # Test with Finnish special character ä
    result1 = search_mo_file(Path("/test/file.mo"), "ä")
    assert len(result1) == 3
    assert ("User", "Käyttäjä", None) in result1
    assert ("Friends", "Ystävät", None) in result1
    assert ("Summer", "Kesä", None) in result1

    # Test with Finnish special character ö
    result2 = search_mo_file(Path("/test/file.mo"), "ö")
    assert len(result2) == 1
    assert result2[0] == ("Night", "Yö", None)

    # Test with partial Finnish word containing special character
    result3 = search_mo_file(Path("/test/file.mo"), "käyt")
    assert len(result3) == 1
    assert result3[0] == ("User", "Käyttäjä", None)
