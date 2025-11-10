import csv
import tempfile
from pathlib import Path

import pytest

from wittrans.functions import write_tsv_output


class TestWriteTsvOutput:
    """Test cases for write_tsv_output function."""

    @pytest.fixture
    def sample_system_results(self):
        """Sample system translation results."""
        return [
            (
                Path("/usr/share/locale/fi/LC_MESSAGES/app1.mo"),
                [
                    ("Hello", "Hei", None),
                    ("Monday", "Maanantai", "weekday"),
                ],
            ),
            (
                Path("/usr/local/share/locale/fi/LC_MESSAGES/app2.mo"),
                [
                    ("Goodbye", "Näkemiin", "greeting"),
                ],
            ),
        ]

    @pytest.fixture
    def sample_user_locale_results(self):
        """Sample user locale translation results."""
        return [
            (
                Path("~/.local/share/locale/fi/LC_MESSAGES/userapp.mo"),
                [
                    ("Save", "Tallenna", "file"),
                ],
            ),
        ]

    @pytest.fixture
    def sample_flatpak_results(self):
        """Sample Flatpak translation results."""
        return [
            (
                Path(
                    "/var/lib/flatpak/app/com.example.App/x86_64/stable/active/files/share/locale/fi/LC_MESSAGES/app.mo"
                ),
                [
                    ("File", "Tiedosto", "menu"),
                    ("Edit", "Muokkaa", "menu"),
                ],
            ),
        ]

    @pytest.fixture
    def sample_kde_results(self):
        """Sample KDE plasmoid translation results."""
        return [
            (
                Path(
                    "/usr/local/share/plasma/plasmoids/test-widget/contents/locale/fi/LC_MESSAGES/plasma_applet_test.mo"
                ),
                [
                    ("Configure", "Määritä", "widget"),
                ],
            ),
        ]

    @pytest.fixture
    def comprehensive_results_by_category(
        self,
        sample_system_results,
        sample_user_locale_results,
        sample_flatpak_results,
        sample_kde_results,
    ):
        """Comprehensive results covering all 8 categories including paths."""
        return {
            "system_locale": {
                "results": sample_system_results,
                "display_name": "System Locale",
                "has_paths": True,
            },
            "user_locale": {
                "results": sample_user_locale_results,
                "display_name": "User Locale",
                "has_paths": True,
            },
            "system_gnome_extensions": {
                "results": [
                    (
                        Path(
                            "/usr/local/share/gnome-shell/extensions/test@example.com/locale/fi/LC_MESSAGES/test.mo"
                        ),
                        [("Preferences", "Asetukset", "extension")],
                    )
                ],
                "display_name": "System GNOME Extensions",
                "has_paths": True,
            },
            "system_kde_plasmoids": {
                "results": sample_kde_results,
                "display_name": "System KDE Plasmoids",
                "has_paths": True,
            },
            "user_gnome_extensions": {
                "results": [
                    (
                        Path(
                            "~/.local/share/gnome-shell/extensions/user@extension.com/locale/fi/LC_MESSAGES/user.mo"
                        ),
                        [("Options", "Valinnat", "user_extension")],
                    )
                ],
                "display_name": "User GNOME Extensions",
                "has_paths": True,
            },
            "user_kde_plasmoids": {
                "results": [
                    (
                        Path(
                            "~/.local/share/plasma/plasmoids/user-widget/contents/locale/fi/LC_MESSAGES/user_widget.mo"
                        ),
                        [("Settings", "Asetukset", "user_widget")],
                    )
                ],
                "display_name": "User KDE Plasmoids",
                "has_paths": True,
            },
            "flatpak_system": {
                "results": sample_flatpak_results,
                "display_name": "System Flatpak",
                "has_paths": True,
            },
            "flatpak_user": {
                "results": [
                    (
                        Path(
                            "~/.local/share/flatpak/app/org.user.App/x86_64/stable/active/files/share/locale/fi/LC_MESSAGES/userapp.mo"
                        ),
                        [("Close", "Sulje", "button")],
                    )
                ],
                "display_name": "User Flatpak",
                "has_paths": True,
            },
        }

    @pytest.fixture
    def empty_results_by_category(self):
        """Empty results structured by category with all 8 categories."""
        return {
            "system_locale": {
                "results": [],
                "display_name": "System Locale",
                "has_paths": False,
            },
            "user_locale": {
                "results": [],
                "display_name": "User Locale",
                "has_paths": False,
            },
            "system_gnome_extensions": {
                "results": [],
                "display_name": "System GNOME Extensions",
                "has_paths": False,
            },
            "system_kde_plasmoids": {
                "results": [],
                "display_name": "System KDE Plasmoids",
                "has_paths": False,
            },
            "user_gnome_extensions": {
                "results": [],
                "display_name": "User GNOME Extensions",
                "has_paths": False,
            },
            "user_kde_plasmoids": {
                "results": [],
                "display_name": "User KDE Plasmoids",
                "has_paths": False,
            },
            "flatpak_system": {
                "results": [],
                "display_name": "System Flatpak",
                "has_paths": False,
            },
            "flatpak_user": {
                "results": [],
                "display_name": "User Flatpak",
                "has_paths": False,
            },
        }

    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".tsv") as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)

    def test_basic_tsv_output(self, temp_file, monkeypatch):
        """Test basic TSV file creation with both system and Flatpak results."""
        monkeypatch.setattr("wittrans.functions.get_language_name", lambda x: "Finnish")

        # Create basic results structure inline
        results_by_category = {
            "system_locale": {
                "results": [
                    (
                        Path("/usr/share/locale/fi/LC_MESSAGES/app1.mo"),
                        [
                            ("Hello", "Hei", None),
                            ("Monday", "Maanantai", "weekday"),
                        ],
                    ),
                    (
                        Path("/usr/share/locale/fi/LC_MESSAGES/app2.mo"),
                        [
                            ("Goodbye", "Näkemiin", "greeting"),
                        ],
                    ),
                ],
                "display_name": "System Locale",
                "has_paths": True,
            },
            "user_locale": {
                "results": [],
                "display_name": "User Locale",
                "has_paths": False,
            },
            "system_gnome_extensions": {
                "results": [],
                "display_name": "System GNOME Extensions",
                "has_paths": False,
            },
            "system_kde_plasmoids": {
                "results": [],
                "display_name": "System KDE Plasmoids",
                "has_paths": False,
            },
            "user_gnome_extensions": {
                "results": [],
                "display_name": "User GNOME Extensions",
                "has_paths": False,
            },
            "user_kde_plasmoids": {
                "results": [],
                "display_name": "User KDE Plasmoids",
                "has_paths": False,
            },
            "flatpak_system": {
                "results": [
                    (
                        Path(
                            "/var/lib/flatpak/app/com.example.App/x86_64/stable/active/files/share/locale/fi/LC_MESSAGES/app.mo"
                        ),
                        [
                            ("File", "Tiedosto", "menu"),
                            ("Edit", "Muokkaa", "menu"),
                        ],
                    ),
                ],
                "display_name": "System Flatpak",
                "has_paths": True,
            },
            "flatpak_user": {
                "results": [],
                "display_name": "User Flatpak",
                "has_paths": False,
            },
        }

        write_tsv_output(
            results_by_category,
            "test_search",
            "fi",
            temp_file,
        )

        # Verify file was created
        assert Path(temp_file).exists()

        # Read and verify content
        with open(temp_file, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f, delimiter="\t")
            rows = list(reader)

        # Check header
        expected_header = [
            "Source Type",
            "File Path",
            "Context",
            "Original Text",
            "Finnish Translation",
        ]
        assert rows[0] == expected_header

        # Check data rows (3 system + 2 flatpak = 5 data rows + 1 header = 6 total)
        assert len(rows) == 6

        # Check first system result
        assert rows[1][0] == "System Locale"
        assert "app1.mo" in rows[1][1]
        assert rows[1][2] == ""  # No context
        assert rows[1][3] == "Hello"
        assert rows[1][4] == "Hei"

    def test_comprehensive_all_paths_coverage(
        self, comprehensive_results_by_category, temp_file, monkeypatch
    ):
        """Test TSV output with results from all 8 categories including new paths."""
        monkeypatch.setattr("wittrans.functions.get_language_name", lambda x: "Finnish")

        write_tsv_output(
            comprehensive_results_by_category, "comprehensive_test", "fi", temp_file
        )

        with open(temp_file, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f, delimiter="\t")
            rows = list(reader)

        # Count actual entries from the test data:
        # system_locale: 3 entries (2 from app1.mo + 1 from app2.mo)
        # user_locale: 1 entry
        # system_gnome_extensions: 1 entry
        # system_kde_plasmoids: 1 entry
        # user_gnome_extensions: 1 entry
        # user_kde_plasmoids: 1 entry
        # flatpak_system: 2 entries (File + Edit from same .mo file)
        # flatpak_user: 1 entry
        # Total: 11 data rows + 1 header = 12 rows
        assert len(rows) == 12

        # Verify all category types are represented
        source_types = {row[0] for row in rows[1:]}  # Skip header
        expected_types = {
            "System Locale",
            "User Locale",
            "System GNOME Extensions",
            "System KDE Plasmoids",
            "User GNOME Extensions",
            "User KDE Plasmoids",
            "System Flatpak",
            "User Flatpak",
        }
        assert source_types == expected_types

        file_paths = [row[1] for row in rows[1:]]

        # Check for new user locale path
        assert any("/.local/share/locale/" in path for path in file_paths)

        # Check for /usr/local/share/gnome-shell/extensions path
        assert any(
            "/usr/local/share/gnome-shell/extensions/" in path for path in file_paths
        )

        # Check for /usr/local/share/plasma/plasmoids path
        assert any("/usr/local/share/plasma/plasmoids/" in path for path in file_paths)

    def test_empty_results(self, empty_results_by_category, temp_file, monkeypatch):
        """Test TSV output with empty results."""
        monkeypatch.setattr("wittrans.functions.get_language_name", lambda x: "Finnish")

        write_tsv_output(empty_results_by_category, "nonexistent", "fi", temp_file)

        # Verify file was created with only header
        with open(temp_file, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f, delimiter="\t")
            rows = list(reader)

        assert len(rows) == 1  # Only header
        expected_header = [
            "Source Type",
            "File Path",
            "Context",
            "Original Text",
            "Finnish Translation",
        ]
        assert rows[0] == expected_header

    def test_new_paths_specific_content(self, temp_file, monkeypatch):
        """Test that the three new specific paths work correctly in TSV output."""
        monkeypatch.setattr("wittrans.functions.get_language_name", lambda x: "Finnish")

        # Focus on paths
        results_by_category = {
            "system_locale": {
                "results": [
                    (
                        Path("/usr/local/share/locale/fi/LC_MESSAGES/manual_app.mo"),
                        [("Install", "Asenna", "action")],
                    )
                ],
                "display_name": "System Locale",
                "has_paths": True,
            },
            "user_locale": {
                "results": [
                    (
                        Path("~/.local/share/locale/fi/LC_MESSAGES/compiled_app.mo"),
                        [("Compile", "Käännä", "build")],
                    )
                ],
                "display_name": "User Locale",
                "has_paths": True,
            },
            "system_gnome_extensions": {
                "results": [],
                "display_name": "System GNOME Extensions",
                "has_paths": False,
            },
            "system_kde_plasmoids": {
                "results": [
                    (
                        Path(
                            "/usr/local/share/plasma/plasmoids/admin-widget/contents/locale/fi/LC_MESSAGES/widget.mo"
                        ),
                        [("Widget", "Vimpain", "kde")],
                    )
                ],
                "display_name": "System KDE Plasmoids",
                "has_paths": True,
            },
            "user_gnome_extensions": {
                "results": [],
                "display_name": "User GNOME Extensions",
                "has_paths": False,
            },
            "user_kde_plasmoids": {
                "results": [],
                "display_name": "User KDE Plasmoids",
                "has_paths": False,
            },
            "flatpak_system": {
                "results": [],
                "display_name": "System Flatpak",
                "has_paths": False,
            },
            "flatpak_user": {
                "results": [],
                "display_name": "User Flatpak",
                "has_paths": False,
            },
        }

        write_tsv_output(results_by_category, "new_paths", "fi", temp_file)

        with open(temp_file, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f, delimiter="\t")
            rows = list(reader)

        # Should have header + 3 rows for specific path examples
        assert len(rows) == 4

        # Verify the three paths are properly categorized
        paths_and_types = [(row[1], row[0]) for row in rows[1:]]

        # Check /usr/local/share/locale path is in System Locale
        usr_local_locale = next(
            (pt for pt in paths_and_types if "/usr/local/share/locale/" in pt[0]), None
        )
        assert usr_local_locale is not None
        assert usr_local_locale[1] == "System Locale"

        # Check ~/.local/share/locale path is in User Locale
        user_local_locale = next(
            (pt for pt in paths_and_types if "/.local/share/locale/" in pt[0]), None
        )
        assert user_local_locale is not None
        assert user_local_locale[1] == "User Locale"

        # Check /usr/local/share/plasma/plasmoids path is in System KDE Plasmoids
        usr_local_kde = next(
            (
                pt
                for pt in paths_and_types
                if "/usr/local/share/plasma/plasmoids/" in pt[0]
            ),
            None,
        )
        assert usr_local_kde is not None
        assert usr_local_kde[1] == "System KDE Plasmoids"
