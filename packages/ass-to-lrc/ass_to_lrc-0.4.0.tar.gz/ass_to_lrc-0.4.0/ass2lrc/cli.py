"""Command-line interface for ASS to LRC conversion."""

import logging
from pathlib import Path
from typing import Annotated

import typer

from . import __version__
from .ass_converter import ASSConverter
from .converter import LRCConverter
from .expander import LRCExpander
from .lrc_parser import LRCParser
from .parser import ASSParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

app = typer.Typer(
    name="ass2lrc",
    help="Convert ASS subtitle files to LRC lyrics format",
    add_completion=False,
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"ass2lrc version {__version__}")
        raise typer.Exit()


@app.command()
def convert(
    input_file: Annotated[
        Path,
        typer.Argument(
            help="Input ASS file path",
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
        ),
    ],
    output_file: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Output LRC file path (default: same as input with .lrc/.elrc extension)",
        ),
    ] = None,
    enhanced: Annotated[
        bool,
        typer.Option(
            "--enhanced/--simple",
            "-e/-s",
            help="Generate enhanced LRC with word timing (default: enhanced)",
        ),
    ] = True,
    compact: Annotated[
        bool,
        typer.Option(
            "--compact",
            "-c",
            help=(
                "Use compact format (multiple timestamps per line). "
                "Warning: not all programs support this."
            ),
        ),
    ] = False,
    line_gap: Annotated[
        float,
        typer.Option(
            "--gap",
            "-g",
            help="Gap in seconds to add between lines (default: 1.0)",
            min=0.0,
        ),
    ] = 1.0,
    include_comments: Annotated[
        bool,
        typer.Option(
            "--comment",
            help="Include ASS comment events as LRC comment lines",
        ),
    ] = False,
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit",
        ),
    ] = None,
) -> None:
    """
    Convert ASS subtitle file to LRC lyrics format.

    By default, generates enhanced LRC (.elrc) with word-level timing from \\k tags.
    Use --simple to generate basic LRC without word timing.
    """
    try:
        # Parse ASS file
        typer.echo(f"Parsing {input_file}...")
        parser = ASSParser(input_file, include_comments=include_comments)
        lyrics = parser.parse_lyrics()

        if not lyrics:
            typer.echo("⚠️  No lyrics found in ASS file", err=True)
            raise typer.Exit(1)

        # Auto-fallback to simple format if no karaoke timing
        if enhanced and not parser.has_karaoke_timing():
            typer.echo(
                "ℹ️  No karaoke timing detected. Automatically using simple format.",
                err=True,
            )
            enhanced = False

        # Determine output file
        if output_file is None:
            extension = ".elrc" if enhanced else ".lrc"
            output_file = input_file.with_suffix(extension)

        # Warn about compact format
        if compact:
            if enhanced:
                typer.echo(
                    "⚠️  Warning: Compact format doesn't support word timing. "
                    "Generating compact LRC without word timing.",
                    err=True,
                )
            else:
                typer.echo(
                    "⚠️  Warning: Compact format may not be supported by all players.",
                    err=True,
                )

        # Convert to LRC
        format_type = "compact " if compact else ""
        typer.echo(f"Converting to {format_type}{'enhanced' if enhanced else 'simple'} LRC...")
        converter = LRCConverter(
            metadata=parser.metadata,
            enhanced=enhanced,
            line_gap=line_gap,
            compact=compact,
            include_comments=include_comments,
        )
        converter.convert(lyrics, output_file)

        typer.echo(f"✓ Successfully converted to {output_file}")
        typer.echo(f"  Lines: {len(lyrics)}")
        if parser.metadata.artist:
            typer.echo(f"  Artist: {parser.metadata.artist}")
        if parser.metadata.lyricist:
            typer.echo(f"  Lyricist: {parser.metadata.lyricist}")

    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def expand(
    input_file: Annotated[
        Path,
        typer.Argument(
            help="Input compact LRC file path",
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
        ),
    ],
    output_file: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Output expanded LRC file path (default: input with _expanded suffix)",
        ),
    ] = None,
) -> None:
    """
    Expand compact LRC format to standard sorted format.

    Converts LRC files with multiple timestamps per line to standard format
    with one timestamp per line, sorted by time.
    """
    try:
        # Determine output file
        if output_file is None:
            stem = input_file.stem
            output_file = input_file.with_stem(f"{stem}_expanded")

        typer.echo(f"Expanding {input_file}...")
        expander = LRCExpander()
        expander.expand(input_file, output_file)

        typer.echo(f"✓ Successfully expanded to {output_file}")

    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def lrc2ass(
    input_file: Annotated[
        Path,
        typer.Argument(
            help="Input LRC file path",
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
        ),
    ],
    output_file: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Output ASS file path (default: same as input with .ass extension)",
        ),
    ] = None,
    with_karaoke: Annotated[
        bool,
        typer.Option(
            "--karaoke/--no-karaoke",
            "-k/-K",
            help="Generate karaoke timing tags from enhanced LRC (default: enabled)",
        ),
    ] = True,
    include_comments: Annotated[
        bool,
        typer.Option(
            "--comment",
            help="Include LRC comment lines as ASS comment events",
        ),
    ] = False,
) -> None:
    """
    Convert LRC lyrics file to ASS subtitle format.

    Converts both simple and enhanced LRC files to ASS format.
    Enhanced LRC with inline timestamps will generate karaoke timing tags.
    """
    try:
        # Parse LRC file
        typer.echo(f"Parsing {input_file}...")
        parser = LRCParser(input_file, include_comments=include_comments)
        lyrics = parser.parse_lyrics()

        if not lyrics:
            typer.echo("⚠️  No lyrics found in LRC file", err=True)
            raise typer.Exit(1)

        # Check for enhanced timing
        if with_karaoke and not parser.has_enhanced_timing():
            typer.echo(
                "ℹ️  No enhanced timing detected. Generating simple ASS format.",
                err=True,
            )
            with_karaoke = False

        # Determine output file
        if output_file is None:
            output_file = input_file.with_suffix(".ass")

        # Convert to ASS
        typer.echo(f"Converting to ASS {'with karaoke tags' if with_karaoke else 'format'}...")
        converter = ASSConverter(
            metadata=parser.metadata,
            with_karaoke=with_karaoke,
            include_comments=include_comments,
        )
        converter.convert(lyrics, output_file)

        typer.echo(f"✓ Successfully converted to {output_file}")
        typer.echo(f"  Lines: {len(lyrics)}")
        if parser.metadata.artist:
            typer.echo(f"  Artist: {parser.metadata.artist}")
        if parser.metadata.title:
            typer.echo(f"  Title: {parser.metadata.title}")

    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
