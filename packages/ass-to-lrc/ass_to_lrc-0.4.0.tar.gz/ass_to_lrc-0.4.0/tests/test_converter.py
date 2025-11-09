"""Tests for LRC converter."""

from pathlib import Path

import pytest

from ass2lrc.converter import LRCConverter
from ass2lrc.models import LyricLine, Metadata, Syllable


@pytest.fixture
def sample_metadata() -> Metadata:
    """Create sample metadata."""
    metadata = Metadata()
    metadata.title = "Test Song"
    metadata.artist = "Test Artist"
    metadata.album = "Test Album"
    metadata.comments = ["Test comment"]
    return metadata


@pytest.fixture
def sample_lyrics() -> list[LyricLine]:
    """Create sample lyrics."""
    return [
        LyricLine(
            start_time=10.0,
            text="First line",
            syllables=[
                Syllable(text="First", start_time=10.0, duration=0.5),
                Syllable(text=" ", start_time=10.5, duration=0.0),
                Syllable(text="line", start_time=10.5, duration=0.5),
            ],
        ),
        LyricLine(
            start_time=12.0,
            text="Second line",
            syllables=[
                Syllable(text="Second", start_time=12.0, duration=0.5),
                Syllable(text=" ", start_time=12.5, duration=0.0),
                Syllable(text="line", start_time=12.5, duration=0.5),
            ],
        ),
    ]


def test_format_timestamp() -> None:
    """Test timestamp formatting."""
    converter = LRCConverter()
    assert converter._format_timestamp(0.0) == "[00:00.00]"
    assert converter._format_timestamp(61.5) == "[01:01.50]"
    assert converter._format_timestamp(125.99) == "[02:05.99]"


def test_format_inline_timestamp() -> None:
    """Test inline timestamp formatting."""
    converter = LRCConverter()
    assert converter._format_inline_timestamp(0.0) == "<00:00.00>"
    assert converter._format_inline_timestamp(61.5) == "<01:01.50>"


def test_generate_metadata_tags(sample_metadata: Metadata) -> None:
    """Test metadata tag generation."""
    converter = LRCConverter(metadata=sample_metadata)
    tags = converter._generate_metadata_tags()

    assert "[ti:Test Song]" in tags
    assert "[ar:Test Artist]" in tags
    assert "[al:Test Album]" in tags
    assert "[#]Test comment" in tags


def test_enhanced_lrc_generation(
    sample_lyrics: list[LyricLine], sample_metadata: Metadata, tmp_path: Path
) -> None:
    """Test enhanced LRC generation."""
    output_file = tmp_path / "test.elrc"
    converter = LRCConverter(metadata=sample_metadata, enhanced=True, line_gap=1.0)
    converter.convert(sample_lyrics, output_file)

    content = output_file.read_text(encoding="utf-8")

    # Check metadata
    assert "[ti:Test Song]" in content
    assert "[ar:Test Artist]" in content

    # Check enhanced timing (inline timestamps)
    assert "<00:10.00>" in content
    assert "<00:10.50>" in content

    # Check gap line
    assert "[00:12.00]" in content


def test_simple_lrc_generation(
    sample_lyrics: list[LyricLine], sample_metadata: Metadata, tmp_path: Path
) -> None:
    """Test simple LRC generation."""
    output_file = tmp_path / "test.lrc"
    converter = LRCConverter(metadata=sample_metadata, enhanced=False, line_gap=1.0)
    converter.convert(sample_lyrics, output_file)

    content = output_file.read_text(encoding="utf-8")

    # Check metadata
    assert "[ti:Test Song]" in content

    # Check no inline timestamps
    assert "<00:10.00>" not in content
    assert "<00:10.50>" not in content

    # Check plain text
    assert "First line" in content
    assert "Second line" in content


def test_compact_format(sample_lyrics: list[LyricLine], tmp_path: Path) -> None:
    """Test compact format generation."""
    # Add duplicate lyric
    lyrics_with_duplicate = sample_lyrics + [
        LyricLine(
            start_time=20.0,
            text="First line",
            syllables=[
                Syllable(text="First", start_time=20.0, duration=0.5),
                Syllable(text=" ", start_time=20.5, duration=0.0),
                Syllable(text="line", start_time=20.5, duration=0.5),
            ],
        ),
    ]

    output_file = tmp_path / "test_compact.lrc"
    converter = LRCConverter(enhanced=False, line_gap=0.0, compact=True)
    converter.convert(lyrics_with_duplicate, output_file)

    content = output_file.read_text(encoding="utf-8")

    # Check that duplicate lyrics have multiple timestamps
    assert "[00:10.00][00:20.00]First line" in content


def test_compact_disables_enhanced(sample_lyrics: list[LyricLine], tmp_path: Path) -> None:
    """Test that compact format disables enhanced word timing."""
    output_file = tmp_path / "test_compact_enhanced.lrc"

    # Request both compact and enhanced (enhanced should be disabled)
    converter = LRCConverter(enhanced=True, line_gap=0.0, compact=True)

    # Enhanced should be automatically disabled
    assert converter.enhanced is False

    converter.convert(sample_lyrics, output_file)
    content = output_file.read_text(encoding="utf-8")

    # Should NOT have inline timestamps (enhanced timing)
    assert "<00:10.00>" not in content
    assert "<00:10.50>" not in content

    # Should have plain text
    assert "First line" in content


def test_no_gap_generation(sample_lyrics: list[LyricLine], tmp_path: Path) -> None:
    """Test LRC generation without gap lines."""
    output_file = tmp_path / "test_nogap.lrc"
    converter = LRCConverter(enhanced=False, line_gap=0.0)
    converter.convert(sample_lyrics, output_file)

    content = output_file.read_text(encoding="utf-8")
    lines = content.strip().split("\n")

    # Count timestamp-only lines (gap lines)
    gap_lines = [line for line in lines if line.startswith("[") and line.endswith("]")]
    # Should only have the final empty line
    assert len([line for line in gap_lines if line != lines[-1]]) == 0


def test_empty_lyrics_list(tmp_path: Path) -> None:
    """Test conversion with empty lyrics list."""
    output_file = tmp_path / "test_empty.lrc"
    converter = LRCConverter(enhanced=False)
    converter.convert([], output_file)

    content = output_file.read_text(encoding="utf-8")
    # Should not have the final timestamp if no lyrics
    assert content.strip() == "" or not content.strip().startswith("[00:")


def test_enhanced_no_word_timing_at_end(sample_lyrics: list[LyricLine], tmp_path: Path) -> None:
    """Test that enhanced LRC doesn't add timing after last syllable."""
    output_file = tmp_path / "test_no_end_timing.elrc"
    converter = LRCConverter(enhanced=True, line_gap=0.0)
    converter.convert([sample_lyrics[0]], output_file)

    content = output_file.read_text(encoding="utf-8")

    # The line should end with the text, not a timestamp
    # Should have: [00:10.00]<00:10.00>First<00:10.50> <00:10.50>line
    # Not: [00:10.00]<00:10.00>First<00:10.50> <00:10.50>line<00:11.00>
    assert not content.rstrip().endswith(">")
