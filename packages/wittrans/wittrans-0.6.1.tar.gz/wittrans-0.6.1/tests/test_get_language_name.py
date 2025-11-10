from pathlib import Path

import pytest

from wittrans.functions import (
    InvalidLanguageCode,
    TranslationDirectoryNotFound,
    TranslationPaths,
    get_language_name,
    validate_language_paths,
)


def test_get_language_name():
    assert get_language_name("fi") == "Finnish"
    assert get_language_name("sv") == "Swedish"
    assert get_language_name("en") == "English"


def test_validate_language_paths_valid():
    test_cases = [
        "fi",
        "fin",
        "fi_FI",
        "fi_FI.utf8",
    ]

    for lang_code in test_cases:
        # validate_language_paths must return a TranslationPaths named tuple
        translation_paths = validate_language_paths(lang_code)

        # Verify it returns the correct type
        assert isinstance(translation_paths, TranslationPaths)

        # Get all paths from all categories
        all_paths = (
            translation_paths.system_locale
            + translation_paths.system_gnome_extensions
            + translation_paths.system_kde_plasmoids
            + translation_paths.user_gnome_extensions
            + translation_paths.user_kde_plasmoids
            + translation_paths.flatpak_system
            + translation_paths.flatpak_user
        )

        # At least one category should contain paths for valid language codes
        assert len(all_paths) > 0, f"No paths found for {lang_code}"

        # Verify all paths are Path objects
        assert all(isinstance(path, Path) for path in all_paths)

        # Test individual categories are lists of Path objects
        for category_paths in translation_paths:
            assert isinstance(category_paths, list)
            assert all(isinstance(path, Path) for path in category_paths)


def test_validate_language_paths_structure():
    """Test that the returned TranslationPaths has the expected structure."""
    translation_paths = validate_language_paths("fi")

    # Verify all expected attributes exist
    expected_attributes = [
        "system_locale",
        "system_gnome_extensions",
        "system_kde_plasmoids",
        "user_gnome_extensions",
        "user_kde_plasmoids",
        "flatpak_system",
        "flatpak_user",
    ]

    for attr in expected_attributes:
        assert hasattr(translation_paths, attr)
        assert isinstance(getattr(translation_paths, attr), list)


def test_validate_language_paths_invalid():
    with pytest.raises(InvalidLanguageCode):
        validate_language_paths("123")

    with pytest.raises(TranslationDirectoryNotFound):
        validate_language_paths("ok")
