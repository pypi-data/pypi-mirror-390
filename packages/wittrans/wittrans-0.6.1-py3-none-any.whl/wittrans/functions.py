"""
Classes and functions used in wittrans.

SPDX-FileCopyrightText: 2024 Jiri Grönroos <jiri.gronroos@iki.fi>

SPDX-License-Identifier: AGPL-3.0-or-later

"""

import argparse
import csv
import locale
import subprocess
import sys
from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import List, NamedTuple, Optional, Set, Tuple

import polib
from rich import print as rprint
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table

from . import __version__
from .language_mappings import (
    iso_639_1,
    iso_639_3,
    iso_639_3_to_1,
    locale_variants,
    regional_variants,
)


class TranslationPaths(NamedTuple):
    """Container for categorized translation paths found on a Linux system."""

    system_locale: List[Path]
    user_locale: List[Path]
    system_gnome_extensions: List[Path]
    system_kde_plasmoids: List[Path]
    user_gnome_extensions: List[Path]
    user_kde_plasmoids: List[Path]
    flatpak_system: List[Path]
    flatpak_user: List[Path]


class TranslationDirectoryNotFound(Exception):
    """Exception raised when translation directory is not found."""

    pass


class InvalidLanguageCode(Exception):
    """Exception raised when language code is invalid."""

    pass


class FlatpakNotInstalled(Exception):
    """Exception raised when Flatpak is not installed."""

    pass


def check_platform() -> None:
    """Check that the platform is Linux."""
    console = Console()
    if sys.platform == "linux" or sys.platform == "linux2":
        pass
    elif sys.platform == "darwin":
        console.print(
            "wittrans must be run on a Linux distribution, macOS is not supported. Exiting."
        )
        sys.exit(1)
    elif sys.platform == "win32":
        console.print(
            "wittrans must be run on a Linux distribution, Windows is not supported. Exiting."
        )
        sys.exit(1)


def get_system_architecture() -> str:
    """
    Get the system architecture using uname.

    Returns:
        String representing system architecture (e.g., 'x86_64', 'aarch64')
    """
    try:
        arch = subprocess.run(
            ["uname", "-m"], capture_output=True, text=True, check=True
        ).stdout.strip()
        return arch
    except subprocess.CalledProcessError:
        # Default to x86_64 if architecture can not be determined
        return "x86_64"


def get_language_name(lang_code: str) -> str:
    """
    Get the full language name from its code.

    Supports:
    1. ISO 639-1 codes (two letters, e.g., "fi", "sv", "en")
    2. ISO 639-2/3 codes (three letters, e.g., "fin", "swe", "eng")
    3. GNU C library locale codes (e.g., "fi_FI.utf8", "zh_CN", "pt_BR")

    Args:
        lang_code: Language code (ISO 639-1, ISO 639-2/3, or full locale code)

    Returns:
        Full language name, or "Unknown (code)" if not found
    """
    # Normalize the input code
    normalized_code = lang_code.lower().strip()

    # Split the code into parts (e.g., "fi_FI.utf8" -> ["fi", "FI", "utf8"])
    parts = normalized_code.split(".")
    locale_parts = parts[0].split("_")
    base_lang = locale_parts[0]

    # 1. Check for known locale variants first
    if len(locale_parts) > 1:
        variant_code = "_".join(locale_parts[:2]).lower()
        if variant_code in locale_variants:
            return locale_variants[variant_code]

    # 2. Check for two-letter ISO 639-1 code
    if len(base_lang) == 2:
        if base_lang in iso_639_1:
            return iso_639_1[base_lang]

    # 3. Check for three-letter ISO 639-2/3 code
    elif len(base_lang) == 3:
        # First try direct mapping for three-letter codes
        if base_lang in iso_639_3:
            return iso_639_3[base_lang]
        # Then try converting to two-letter code
        two_letter = iso_639_3_to_1.get(base_lang)
        if two_letter and two_letter in iso_639_1:
            return iso_639_1[two_letter]

    # 4. Try the locale system as fallback
    try:
        current_locale = locale.getlocale()
        try:
            locale.setlocale(locale.LC_ALL, normalized_code)
            language_name = locale.nl_langinfo(locale.LANGNAME)
            if language_name and language_name.strip():
                return language_name.title()
        except (locale.Error, AttributeError):
            pass
        finally:
            try:
                locale.setlocale(locale.LC_ALL, current_locale)
            except locale.Error:
                locale.setlocale(locale.LC_ALL, "")
    except Exception:
        pass

    # 5. Last resort: return unknown
    return f"Unknown ({normalized_code})"


def validate_language_paths(
    lang_code: str, include_flatpak: bool = True
) -> TranslationPaths:
    """
    Validate and return existing translation paths categorized by source type.

    Supports:
    1. ISO 639-1 codes (two letters, e.g., "fi", "sv", "en")
    2. ISO 639-2/3 codes (three letters, e.g., "fin", "swe", "eng")
    3. GNU C library locale codes (e.g., "fi_FI.utf8", "zh_CN", "pt_BR")

    Searches the following paths:
    - System translations: /usr/share/locale/, /usr/share/locale-langpack/, /usr/local/share/locale/
    - User translations: ~/.local/share/locale/
    - System GNOME Shell extensions: /usr/share/gnome-shell/extensions/, /usr/local/share/gnome-shell/extensions/
    - System KDE Plasmoids: /usr/share/plasma/plasmoids/, /usr/local/share/plasma/plasmoids/
    - User GNOME Shell extensions: ~/.local/share/gnome-shell/extensions/
    - User KDE Plasmoids: ~/.local/share/plasma/plasmoids/
    - Flatpak applications and runtimes (system-wide and user-specific) - if include_flatpak is True

    Args:
        lang_code: Language code (ISO 639-1, ISO 639-2/3, or full locale code)
        include_flatpak: Whether to search Flatpak applications (default: True)

    Returns:
        TranslationPaths named tuple with categorized paths

    Raises:
        InvalidLanguageCode: If language code is invalid
        TranslationDirectoryNotFound: If no translation directories exist
    """

    # Normalize the input code
    normalized_code = lang_code.lower().strip()

    # Split the code into parts (e.g., "fi_FI.utf8" -> ["fi", "FI", "utf8"])
    parts = normalized_code.split(".")
    locale_parts = parts[0].split("_")
    base_lang = locale_parts[0]

    # Validate the base language code
    if not base_lang.isalpha() or not (2 <= len(base_lang) <= 3):
        raise InvalidLanguageCode(
            f"Invalid language code: '{lang_code}'. The language code must be "
            "a two or three-letter ISO-639 code or locale (e.g., 'fi', 'fin', 'zh_CN')."
        )

    # Build list of codes to search for
    search_codes = set()

    # 1. Add the original code first (if it's a full locale code)
    if len(locale_parts) > 1:
        search_codes.add("_".join(locale_parts[:2]).lower())

    # 2. Check for regional variants
    if base_lang in regional_variants:
        search_codes.update(regional_variants[base_lang])

    # 3. Add base language code
    if len(base_lang) == 2:
        # For 2-letter codes, add as is
        search_codes.add(base_lang)
    elif len(base_lang) == 3:
        # For 3-letter codes, try to map to 2-letter code first
        two_letter = iso_639_3_to_1.get(base_lang)
        if two_letter:
            search_codes.add(two_letter)
        else:
            # If no 2-letter mapping exists, use the 3-letter code
            search_codes.add(base_lang)

    # Initialize result containers
    system_locale_paths = []
    user_locale_paths = []
    system_gnome_paths = []
    system_kde_paths = []
    user_gnome_paths = []
    user_kde_paths = []

    # Build system locale paths
    for code in search_codes:
        potential_paths = [
            Path(f"/usr/share/locale-langpack/{code}/LC_MESSAGES"),
            Path(f"/usr/share/locale/{code}/LC_MESSAGES"),
            Path(f"/usr/local/share/locale/{code}/LC_MESSAGES"),
        ]
        system_locale_paths.extend([p for p in potential_paths if p.exists()])

    # Build user locale paths
    for code in search_codes:
        potential_paths = [
            Path.home() / f".local/share/locale/{code}/LC_MESSAGES",
        ]
        user_locale_paths.extend([p for p in potential_paths if p.exists()])

    # Build system GNOME Shell extensions paths
    system_gnome_bases = [
        Path("/usr/share/gnome-shell/extensions"),  # System-installed
        Path(
            "/usr/local/share/gnome-shell/extensions"
        ),  # Not installed by package manager
    ]

    for gnome_base in system_gnome_bases:
        if gnome_base.exists():
            for extension_dir in gnome_base.iterdir():
                if extension_dir.is_dir():
                    for code in search_codes:
                        extension_locale_path = (
                            extension_dir / f"locale/{code}/LC_MESSAGES"
                        )
                        if extension_locale_path.exists():
                            system_gnome_paths.append(extension_locale_path)

    # Build user GNOME Shell extensions paths
    user_gnome_base = Path.home() / ".local/share/gnome-shell/extensions"
    if user_gnome_base.exists():
        for extension_dir in user_gnome_base.iterdir():
            if extension_dir.is_dir():
                for code in search_codes:
                    extension_locale_path = extension_dir / f"locale/{code}/LC_MESSAGES"
                    if extension_locale_path.exists():
                        user_gnome_paths.append(extension_locale_path)

    # Build system KDE Plasmoids paths
    system_kde_bases = [
        Path("/usr/share/plasma/plasmoids"),  # System-installed
        Path("/usr/local/share/plasma/plasmoids"),  # Not installed by package manager
    ]

    for kde_base in system_kde_bases:
        if kde_base.exists():
            for plasmoid_dir in kde_base.iterdir():
                if plasmoid_dir.is_dir():
                    for code in search_codes:
                        plasmoid_locale_path = (
                            plasmoid_dir / f"contents/locale/{code}/LC_MESSAGES"
                        )
                        if plasmoid_locale_path.exists():
                            system_kde_paths.append(plasmoid_locale_path)

    # Build user KDE Plasmoids paths
    user_kde_base = Path.home() / ".local/share/plasma/plasmoids"
    if user_kde_base.exists():
        for plasmoid_dir in user_kde_base.iterdir():
            if plasmoid_dir.is_dir():
                for code in search_codes:
                    plasmoid_locale_path = (
                        plasmoid_dir / f"contents/locale/{code}/LC_MESSAGES"
                    )
                    if plasmoid_locale_path.exists():
                        user_kde_paths.append(plasmoid_locale_path)

    # Get Flatpak paths (categorized by system/user) - only if enabled
    if include_flatpak:
        flatpak_system_paths, flatpak_user_paths = (
            get_flatpak_translation_paths_categorized(search_codes)
        )
    else:
        flatpak_system_paths = []
        flatpak_user_paths = []

    # Create the result tuple
    result = TranslationPaths(
        system_locale=system_locale_paths,
        user_locale=user_locale_paths,
        system_gnome_extensions=system_gnome_paths,
        system_kde_plasmoids=system_kde_paths,
        user_gnome_extensions=user_gnome_paths,
        user_kde_plasmoids=user_kde_paths,
        flatpak_system=flatpak_system_paths,
        flatpak_user=flatpak_user_paths,
    )

    # Check if any translations were found
    total_paths = sum(len(paths) for paths in result)

    if total_paths == 0:
        try:
            language_name = get_language_name(lang_code)
        except Exception:
            language_name = lang_code

        error_msg = [
            f"No translation directories found for {language_name} ({lang_code}).",
            "\nAttempted to find translations using these codes: "
            + ", ".join(sorted(search_codes)),
            "\nSearched in the following categories:",
            "- System locale directories",
            "- User locale directories",
            "- System GNOME Shell extensions",
            "- System KDE Plasmoids",
            "- User GNOME Shell extensions",
            "- User KDE Plasmoids",
            "- Flatpak applications (system and user)",
        ]

        raise TranslationDirectoryNotFound("\n".join(error_msg))

    return result


def get_flatpak_translation_paths_categorized(
    search_codes: Set[str],
) -> Tuple[List[Path], List[Path]]:
    """
    Get translation paths for installed Flatpak applications and runtimes, categorized by system/user.

    Args:
        search_codes: Set of language codes to search for

    Returns:
        Tuple of (system_flatpak_paths, user_flatpak_paths)
    """
    system_paths = []
    user_paths = []
    system_arch = get_system_architecture()

    try:
        # Check if Flatpak is installed
        subprocess.run(
            ["flatpak", "--version"], capture_output=True, text=True, check=True
        )

        # System-wide Flatpak paths
        system_flatpak_bases = [
            Path("/var/lib/flatpak/app"),
            Path("/var/lib/flatpak/runtime"),
        ]
        for base in system_flatpak_bases:
            if base.exists():
                paths = get_flatpak_paths_from_base(base, search_codes, system_arch)
                system_paths.extend(paths)

        # User-specific Flatpak paths
        user_flatpak_bases = [
            Path.home() / ".local/share/flatpak/app",
            Path.home() / ".local/share/flatpak/runtime",
        ]
        for base in user_flatpak_bases:
            if base.exists():
                paths = get_flatpak_paths_from_base(base, search_codes, system_arch)
                user_paths.extend(paths)

    except (subprocess.CalledProcessError, FileNotFoundError):
        pass  # Flatpak not installed

    return system_paths, user_paths


def get_flatpak_paths_from_base(
    base_path: Path, search_codes: Set[str], system_arch: str
) -> List[Path]:
    """
    Helper function to extract Flatpak translation paths from a base directory.

    Args:
        base_path: Base Flatpak directory path
        search_codes: Set of language codes to search for
        system_arch: System architecture

    Returns:
        List of existing translation paths
    """
    translation_paths = []

    for app_dir in base_path.iterdir():
        if not app_dir.is_dir():
            continue

        # Check for architecture-specific directories
        arch_dirs = [app_dir / system_arch]
        if system_arch != "x86_64":
            arch_dirs.append(app_dir / "x86_64")

        for arch_dir in arch_dirs:
            if not arch_dir.exists():
                continue

            # Check stable/active installation
            active_dir = arch_dir / "stable/active"
            if not active_dir.exists():
                continue

            for lang_code in search_codes:
                # Common translation directory patterns
                possible_paths = [
                    # Standard app paths
                    active_dir / f"files/share/locale/{lang_code}/LC_MESSAGES",
                    active_dir / f"files/locale/{lang_code}/LC_MESSAGES",
                    # Runtime-specific paths
                    active_dir / f"files/{lang_code}/share/{lang_code}/LC_MESSAGES",
                    active_dir / f"files/share/{lang_code}/LC_MESSAGES",
                    # Additional runtime paths
                    active_dir / f"files/share/runtime/locale/{lang_code}/LC_MESSAGES",
                    active_dir / f"files/{lang_code}/share/locale/LC_MESSAGES",
                    # Some apps might use different patterns
                    # active_dir / f"files/share/{lang_code}/LC_MESSAGES",
                    active_dir / f"files/{lang_code}/LC_MESSAGES",
                ]

                translation_paths.extend([p for p in possible_paths if p.exists()])

    return translation_paths


def get_flatpak_installation_dirs() -> Set[Path]:
    """
    Get all Flatpak installation directory paths (system-wide and user-specific).

    Returns:
        Set of paths to Flatpak installation directories
    """
    paths = set()

    try:
        # Check if Flatpak is installed
        subprocess.run(
            ["flatpak", "--version"], capture_output=True, text=True, check=True
        )

        # System-wide installation paths
        system_paths = [Path("/var/lib/flatpak/app"), Path("/var/lib/flatpak/runtime")]
        paths.update(p for p in system_paths if p.exists())

        # User-specific installation paths
        user_paths = [
            Path.home() / ".local/share/flatpak/app",
            Path.home() / ".local/share/flatpak/runtime",
        ]
        paths.update(p for p in user_paths if p.exists())

        return paths

    except (subprocess.CalledProcessError, FileNotFoundError):
        return set()


def find_mo_files(base_path: Path) -> List[Path]:
    """
    Find all .mo files in the given directory and its subdirectories.

    Args:
        base_path: Directory path to search in

    Returns:
        List of paths to .mo files
    """
    try:
        return list(base_path.rglob("*.mo"))
    except PermissionError:
        rprint(
            f"[yellow]Warning: Permission denied accessing some files in {base_path}[/yellow]"
        )
        return []
    except Exception as e:
        rprint(f"[yellow]Warning: Error scanning {base_path}: {str(e)}[/yellow]")
        return []


def search_mo_file_wrapper(args):
    """
    Wrapper function to enable `search_mo_file` to be used with `multiprocessing.Pool.imap`.

    This function unpacks a tuple of arguments and passes them to `search_mo_file`.
    The `multiprocessing.Pool.imap` method can only accept functions that take a single
    argument, so this wrapper combines the `file_path` and `search_term` into a single tuple
    parameter that gets unpacked.

    Args:
        args (Tuple[Path, str]): A tuple containing:
            - file_path (Path): Path to the .mo file to search
            - search_term (str): Text to search for in the .mo file

    Returns:
        Tuple[Path, List[Tuple[str, str, Optional[str]]]]: A tuple containing:
            - file_path (Path): The original file path that was searched
            - matches (List): List of translation matches found in the file. Each match
              is a tuple of (original_text, translated_text, optional_context).
              Returns an empty list if no matches are found.

    Note:
        This function always returns a tuple with the file path and match results,
        even when no matches are found (in which case the match list will be empty).
    """
    file_path, search_term = args
    return (file_path, search_mo_file(file_path, search_term))


def search_directory(
    base_path: Path, search_term: str, progress: Progress
) -> List[Tuple[Path, List[Tuple[str, str, Optional[str]]]]]:
    """
    Search for translations in all .mo files in a directory using multiprocessing.

    Uses a process pool to search each .mo file in parallel, updating the progress bar
    incrementally as each file is processed.

    Args:
        base_path: Directory path to search in.
        search_term: Text to search for (case-insensitive, in both original and translated text).
        progress: Progress bar instance for reporting search progress.

    Returns:
        List of tuples, each containing:
            - Path: Path to the .mo file where matches were found.
            - List[Tuple[str, str, Optional[str]]]: List of matches, each as a tuple of
              (original text, translation, optional context).

        If no .mo files are found in the directory, returns an empty list, and no progress task is created.
    """
    mo_files = find_mo_files(base_path)
    if not mo_files:
        return []

    results = []
    task = progress.add_task(f"[cyan]Searching in {base_path}...", total=len(mo_files))

    # Use a process pool with imap for incremental results
    with Pool(processes=cpu_count()) as pool:
        # Prepare arguments for the pool
        args_list = [(file, search_term) for file in mo_files]

        # Use imap to get results as they complete
        for file_path, matches in pool.imap(search_mo_file_wrapper, args_list):
            if matches:  # Add to results if there are matches
                results.append((file_path, matches))
            progress.advance(task)  # Advance progress for each completed file

    return results


def search_mo_file(
    file_path: Path, search_term: str
) -> List[Tuple[str, str, Optional[str]]]:
    """
    Search for translations in a single .mo file.

    Args:
        file_path: Path to the .mo file
        search_term: Text to search for

    Returns:
        List of tuples containing (original, translation, context) triples
    """
    try:
        mo = polib.mofile(str(file_path), encoding="utf8")
        matches = []

        for entry in mo:
            if (
                search_term.lower() in entry.msgid.lower()
                or search_term.lower() in entry.msgstr.lower()
            ):
                matches.append((entry.msgid, entry.msgstr, entry.msgctxt))

        return matches
    except Exception as e:
        rprint(f"[red]Error processing file {file_path}: {str(e)}[/red]")
        return []


def display_results(
    results: List[Tuple[Path, List[Tuple[str, str, Optional[str]]]]],
    search_term: str,
    lang_code: str,
    source_type: str,
    indicate: bool = False,
) -> None:
    """
    Display search results in a formatted table.
    Args:
        results: List of (file_path, matches) pairs to display
        search_term: The original search term
        lang_code: Language code being searched
        source_type: Type of translation source (e.g. "System" or "Flatpak")
        indicate: Whether to indicate/highlight search term matches
    """
    language_name = get_language_name(lang_code)
    console = Console()
    if not results:
        console.print(
            Panel(
                f"[yellow]No matches found for:[/yellow] [bold red]'{escape(search_term)}'[/bold red]"
                + f" in {source_type} {language_name} translations",
                title=f"{source_type} Search Results",
                border_style="yellow",
            )
        )
        return
    total_matches = sum(len(matches) for _, matches in results)
    console.print(
        Panel(
            f"[green]Found {total_matches} matches for:[/green] "
            + f"[bold red]'{escape(search_term)}'[/bold red]"
            + f" in {source_type} {language_name} translations",
            title=f"{source_type} Search Results",
            border_style="green",
        )
    )
    table = Table(title=f"{language_name} Translation Matches ({source_type})")
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Context", style="magenta")
    table.add_column("Original Text", style="green")
    table.add_column(f"{language_name} Translation", style="yellow")

    for file_path, matches in results:
        for original, translation, context in matches:
            context_escaped = escape(context) if context else ""

            # Apply highlighting only if enabled
            if indicate:
                search_term_lower = search_term.lower()

                if search_term_lower in original.lower():
                    original_highlighted = _highlight_text(original, search_term)
                else:
                    original_highlighted = escape(original)

                if search_term_lower in translation.lower():
                    translation_highlighted = _highlight_text(translation, search_term)
                else:
                    translation_highlighted = escape(translation)
            else:
                # No highlighting
                original_highlighted = escape(original)
                translation_highlighted = escape(translation)

            table.add_row(
                str(file_path),
                context_escaped,
                original_highlighted,
                translation_highlighted,
            )
    console.print(table)


def _highlight_text(text: str, search_term: str) -> str:
    """
    Highlight occurrences of search_term in text.

    Args:
        text: The original text
        search_term: The term to highlight (case-insensitive)

    Returns:
        Text with Rich markup highlighting applied (escaped)
    """
    result = []
    search_lower = search_term.lower()
    text_lower = text.lower()

    last_pos = 0
    pos = 0

    while pos < len(text):
        # Find next occurrence
        idx = text_lower.find(search_lower, pos)
        if idx == -1:
            # No more matches, append rest of text (escaped)
            result.append(escape(text[last_pos:]))
            break

        # Append text before match (escaped)
        if idx > last_pos:
            result.append(escape(text[last_pos:idx]))

        # Append highlighted match (escaped)
        match_text = text[idx : idx + len(search_term)]
        result.append(f"[bold reverse]{escape(match_text)}[/bold reverse]")

        # Move position forward
        last_pos = idx + len(search_term)
        pos = last_pos

    return "".join(result)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Search for translated strings in Linux distribution locale files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Looking for "Monday" in different languages:

  %(prog)s "maanantai" fi            # Finnish (2-letter ISO-639 code)
  %(prog)s "maanantai" fin           # Finnish (3-letter ISO-639 code)
  %(prog)s "maanantai" fi_FI         # Finnish (C locale code)
  %(prog)s "segunda-feira" pt_BR     # Brazilian Portuguese
  %(prog)s "lunes" es                # Spanish
  %(prog)s "星期一" zh_CN            # Simplified Chinese

Additional options:

  %(prog)s "lunes" es -i             # Highlight search results
  %(prog)s "lunes" es --no-flatpak   # Skip Flatpak applications (faster)
  %(prog)s "lunes" es -o tsv         # Export to TSV file
  %(prog)s "星期一" zh_CN -o tsv --output-file chinese_monday.tsv
                                     # Custom output filename

Run 'locale -a' in terminal to see all available locale codes on your system.
        """,
    )
    parser.add_argument(
        "search_term",
        help="Text to search for (case-insensitive search in both original and translated text)",
    )
    parser.add_argument(
        "language_code",
        help="Language code: ISO-639-1 (2-letter), ISO-639-2/3 (3-letter), or C locale code (e.g., fi, fin, fi_FI, zh_CN)",
    )
    parser.add_argument(
        "-i",
        "--indicate",
        action="store_true",
        help="Indicate/highlight search term matches in output",
    )
    parser.add_argument(
        "-f",
        "--no-flatpak",
        action="store_true",
        help="Skip searching Flatpak applications (faster search)",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="FORMAT",
        choices=["tsv"],
        help="Output format: tsv (tab-separated values file). When specified, results are written to [search_term]_[language_code].tsv",
    )
    parser.add_argument(
        "--output-file",
        metavar="FILE",
        help="Custom output filename (used with -o option). If not specified, auto-generated filename is used.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser.parse_args()


def write_tsv_output(
    results_by_category: dict,
    search_term: str,
    lang_code: str,
    output_file: str,
) -> None:
    """
    Write search results to a TSV file with UTF-8 encoding.

    Args:
        results_by_category: Dictionary containing results categorized by source type
        search_term: The original search term
        lang_code: Language code being searched
        output_file: Path to the output TSV file
    """
    language_name = get_language_name(lang_code)

    try:
        # Use UTF-8 with BOM for better compatibility
        with open(output_file, "w", newline="", encoding="utf-8-sig") as tsvfile:
            writer = csv.writer(
                tsvfile,
                delimiter="\t",
                quoting=csv.QUOTE_MINIMAL,
                lineterminator="\n",  # Ensure consistent line endings
            )

            # Write header column names
            writer.writerow(
                [
                    "Source Type",
                    "File Path",
                    "Context",
                    "Original Text",
                    f"{language_name} Translation",
                ]
            )

            # Safely handle text encoding
            def safe_text(text: str) -> str:
                """Ensure text is properly encoded and handle any problematic characters."""
                if not text:
                    return ""
                # Replace any problematic characters that might cause issues
                return text.replace("\x00", "").strip()

            # Write results for each category
            # for category_key, category_data in results_by_category.items():
            for _category_key, category_data in results_by_category.items():
                source_type = category_data["display_name"]
                category_results = category_data["results"]

                for file_path, matches in category_results:
                    # matches is a list of (original, translation, context) tuples
                    for original, translation, context in matches:
                        writer.writerow(
                            [
                                source_type,
                                str(file_path),
                                safe_text(context) if context else "",
                                safe_text(original),
                                safe_text(translation),
                            ]
                        )

    except UnicodeEncodeError as e:
        console = Console()
        console.print(
            Panel(
                f"Unicode encoding error writing to file '{output_file}': {str(e)}\n"
                "Some characters could not be encoded. Try using a different filename or check the translation data.",
                title="[red]Error: Unicode Encoding Failed[/red]",
                border_style="red",
            )
        )
        sys.exit(1)
    except IOError as e:
        console = Console()
        console.print(
            Panel(
                f"Error writing to file '{output_file}': {str(e)}",
                title="[red]Error: File Write Failed[/red]",
                border_style="red",
            )
        )
        sys.exit(1)
