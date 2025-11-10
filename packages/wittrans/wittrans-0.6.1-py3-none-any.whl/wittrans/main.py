#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
wittrans

A command-line tool to search for translated strings and source messages in localization files used by Linux distributions.

Website: https://codeberg.org/artnay/wittrans

SPDX-FileCopyrightText: 2024 Jiri Grönroos <jiri.gronroos@iki.fi>

SPDX-License-Identifier: AGPL-3.0-or-later
"""

import sys

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .functions import (
    InvalidLanguageCode,
    TranslationDirectoryNotFound,
    check_platform,
    display_results,
    get_language_name,
    parse_arguments,
    search_directory,
    validate_language_paths,
    write_tsv_output,
)


def main() -> None:
    """Main function to run the translation search."""
    console = Console()
    check_platform()

    try:
        # Parse command line arguments
        args = parse_arguments()

        search_term = args.search_term
        lang_code = args.language_code.lower()

        # Validate language code and get existing paths for all translation sources
        translation_paths = validate_language_paths(
            lang_code, include_flatpak=not args.no_flatpak
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            # Search all translation categories
            results_by_category = {}

            # Define category mapping for display purposes
            categories = [
                ("system_locale", "System Locale"),
                ("user_locale", "User Locale"),
                ("system_gnome_extensions", "System GNOME Extensions"),
                ("system_kde_plasmoids", "System KDE Plasmoids"),
                ("user_gnome_extensions", "User GNOME Extensions"),
                ("user_kde_plasmoids", "User KDE Plasmoids"),
                ("flatpak_system", "System Flatpak"),
                ("flatpak_user", "User Flatpak"),
            ]

            for category_key, display_name in categories:
                category_paths = getattr(translation_paths, category_key)
                category_results = []

                for path in category_paths:
                    results = search_directory(path, search_term, progress)
                    category_results.extend(results)

                results_by_category[category_key] = {
                    "results": category_results,
                    "display_name": display_name,
                    "has_paths": len(category_paths) > 0,
                }

        # Calculate total matches
        total_matches = sum(
            len(matches)
            for category_data in results_by_category.values()
            for _, matches in category_data["results"]
        )

        if total_matches == 0:
            language_name = get_language_name(lang_code)
            console.print(
                Panel(
                    f"[yellow]No matches found for:[/yellow] [bold red]'{search_term}'[/bold red] "
                    f"in {language_name} translations",
                    title="Search Results",
                    border_style="yellow",
                )
            )

            # Even if there are no search results, create empty TSV file if requested
            if args.output == "tsv":
                if args.output_file:
                    output_filename = args.output_file
                else:
                    # Generate filename from search term and language code
                    safe_search_term = "".join(
                        c for c in search_term if c.isalnum() or c in (" ", "-", "_")
                    ).strip()
                    safe_search_term = safe_search_term.replace(" ", "_")[
                        :20
                    ]  # Limit length
                    output_filename = f"{safe_search_term}_{lang_code}.tsv"

                write_tsv_output(
                    results_by_category,
                    search_term,
                    lang_code,
                    output_filename,
                )
                console.print(
                    f"[green]Empty results written to:[/green] {output_filename}"
                )

            sys.exit(0)

        # Handle output format
        if args.output == "tsv":
            if args.output_file:
                output_filename = args.output_file
            else:
                # Generate filename from search term and language code
                safe_search_term = "".join(
                    c for c in search_term if c.isalnum() or c in (" ", "-", "_")
                ).strip()
                safe_search_term = safe_search_term.replace(" ", "_")[
                    :20
                ]  # Limit length
                output_filename = f"{safe_search_term}_{lang_code}.tsv"

            write_tsv_output(
                results_by_category, search_term, lang_code, output_filename
            )
            console.print(f"[green]Results written to:[/green] {output_filename}")
            console.print(f"[green]Total matches found:[/green] {total_matches}")
        else:
            # Display results in console by category
            first_section = True
            for category_key, display_name in categories:
                category_data = results_by_category[category_key]

                # Only display categories that have results or paths
                if category_data["results"] or category_data["has_paths"]:
                    if not first_section:
                        console.print("\n")  # Add spacing between sections

                    display_results(
                        category_data["results"],
                        search_term,
                        lang_code,
                        display_name,
                        args.indicate,
                    )
                    first_section = False

    except TranslationDirectoryNotFound as e:
        console.print(
            Panel(
                str(e),
                title="[red]Error: Translation Directory Not Found[/red]",
                border_style="red",
            )
        )
        sys.exit(1)
    except InvalidLanguageCode as e:
        console.print(
            Panel(
                str(e),
                title="[red]Error: Invalid Language Code[/red]",
                border_style="red",
            )
        )
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Search cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(
            Panel(
                f"An unexpected error occurred: {str(e)}",
                title="[red]Error[/red]",
                border_style="red",
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
