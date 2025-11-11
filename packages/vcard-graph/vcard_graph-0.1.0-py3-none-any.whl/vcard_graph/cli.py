"""Command-line interface for vcard-graph."""

import logging
from pathlib import Path
from typing import List

import click

from vcard_graph.graph import VCardGraph
from vcard_graph.parser import VCardParser


@click.command()
@click.argument(
    "paths",
    nargs=-1,
    type=click.Path(exists=True, path_type=Path),
    required=True,
)
@click.option(
    "-o",
    "--output",
    default="vcard_graph.html",
    help="Output HTML file path",
    type=str,
)
@click.option(
    "-d",
    "--directory",
    is_flag=True,
    help="Treat paths as directories and parse all vCard files within",
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help="Suppress warnings about unmatched relations",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose logging",
)
def main(paths: tuple[Path, ...], output: str, directory: bool, quiet: bool, verbose: bool) -> None:
    """Visualize vCard contacts as an interactive graph.

    PATHS can be one or more vCard files (.vcf or .vcard) or directories
    containing vCard files (when using --directory flag).

    Example:
        vcard-graph contacts.vcf -o graph.html
        vcard-graph contact1.vcf contact2.vcf contact3.vcf
        vcard-graph ~/contacts/ --directory
        vcard-graph contacts.vcf --quiet  # Suppress warnings
    """
    # Configure logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s",
    )

    parser = VCardParser()

    # Parse the files
    path_list = list(paths)
    if directory:
        click.echo(f"Parsing vCard files from {len(path_list)} directories...")
        for path in path_list:
            if path.is_dir():
                parser.parse_directory(path)
            else:
                click.echo(f"Warning: {path} is not a directory, skipping.", err=True)
    else:
        click.echo(f"Parsing {len(path_list)} vCard files...")
        file_paths: List[Path] = []
        for path in path_list:
            if path.is_file():
                file_paths.append(path)
            else:
                click.echo(f"Warning: {path} is not a file, skipping.", err=True)
        parser.parse_files(file_paths)

    # Check if we parsed any contacts
    contacts = parser.get_all_contacts()
    if not contacts:
        click.echo("Error: No contacts found in the provided files.", err=True)
        raise click.Abort()

    click.echo(f"Found {len(contacts)} contacts.")

    # Build and visualize the graph
    graph = VCardGraph(warn_unmatched=not quiet)
    graph.build_from_parser(parser)

    stats = graph.get_stats()
    click.echo("Graph statistics:")
    click.echo(f"  People: {stats['people']}")
    click.echo(f"  Organizations: {stats['organizations']}")
    click.echo(f"  Relationships: {stats['relationships']}")
    if stats["unmatched_relations"] > 0:
        click.echo(f"  Unmatched relations: {stats['unmatched_relations']}")

    click.echo("Creating visualization...")
    graph.visualize(output)
    click.echo(f"Done! Open {output} in your browser to view the graph.")


if __name__ == "__main__":
    main()
