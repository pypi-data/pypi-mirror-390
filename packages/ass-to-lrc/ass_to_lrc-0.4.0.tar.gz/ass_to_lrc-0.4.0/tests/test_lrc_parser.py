"""Tests for LRC parser."""

from pathlib import Path

import pytest

from ass2lrc.lrc_parser import LRCParser


@pytest.fixture
def sample_lrc_file(tmp_path: Path) -> Path:
    """Create a sample LRC file for testing."""
    lrc_file = tmp_path / "test.lrc"
    lrc_content = """[ti:Test Song]
[ar:Test Artist]
[al:Test Album]
[lr:Test Lyricist]
[00:10.00]Simple line
[00:15.50]Another line
[00:20.00]<00:20.00>Enhanced <00:20.50>line <00:21.00>here
[00:25.00]
"""
    lrc_file.write_text(lrc_content, encoding="utf-8")
    return lrc_file


def test_parser_initialization(sample_lrc_file: Path) -> None:
    """Test LRC parser initialization."""
    parser = LRCParser(sample_lrc_file)
    assert parser.file_path == sample_lrc_file
    assert parser.metadata is not None


def test_parse_metadata(sample_lrc_file: Path) -> None:
    """Test metadata parsing."""
    parser = LRCParser(sample_lrc_file)
    assert parser.metadata.title == "Test Song"
    assert parser.metadata.artist == "Test Artist"
    assert parser.metadata.album == "Test Album"
    assert parser.metadata.lyricist == "Test Lyricist"


def test_parse_simple_lyrics(sample_lrc_file: Path) -> None:
    """Test parsing simple LRC lines."""
    parser = LRCParser(sample_lrc_file)
    lyrics = parser.parse_lyrics()

    assert len(lyrics) == 3  # Empty lines are skipped
    assert lyrics[0].start_time == 10.0
    assert lyrics[0].text == "Simple line"
    assert lyrics[1].start_time == 15.5
    assert lyrics[1].text == "Another line"


def test_parse_enhanced_lyrics(sample_lrc_file: Path) -> None:
    """Test parsing enhanced LRC with inline timestamps."""
    parser = LRCParser(sample_lrc_file)
    lyrics = parser.parse_lyrics()

    enhanced_line = lyrics[2]
    assert enhanced_line.start_time == 20.0
    assert enhanced_line.text == "Enhanced line here"
    assert len(enhanced_line.syllables) == 3
    assert enhanced_line.syllables[0].text == "Enhanced "
    assert enhanced_line.syllables[0].start_time == 20.0
    assert enhanced_line.syllables[0].duration == 0.5
    assert enhanced_line.syllables[1].text == "line "
    assert enhanced_line.syllables[1].start_time == 20.5
    assert enhanced_line.syllables[1].duration == 0.5


def test_has_enhanced_timing(sample_lrc_file: Path) -> None:
    """Test detection of enhanced timing."""
    parser = LRCParser(sample_lrc_file)
    assert parser.has_enhanced_timing() is True


def test_simple_lrc_no_enhanced_timing(tmp_path: Path) -> None:
    """Test simple LRC without enhanced timing."""
    lrc_file = tmp_path / "simple.lrc"
    lrc_content = """[ti:Simple Song]
[00:10.00]Line one
[00:15.00]Line two
"""
    lrc_file.write_text(lrc_content, encoding="utf-8")

    parser = LRCParser(lrc_file)
    assert parser.has_enhanced_timing() is False


def test_parse_timestamp() -> None:
    """Test timestamp parsing."""
    parser = LRCParser.__new__(LRCParser)

    assert parser._parse_timestamp("[01:23.45]") == 83.45
    assert parser._parse_timestamp("<02:30.00>") == 150.0
    assert parser._parse_timestamp("[00:00.00]") == 0.0


def test_lyrics_sorted_by_time(tmp_path: Path) -> None:
    """Test that lyrics are sorted by time."""
    lrc_file = tmp_path / "unsorted.lrc"
    lrc_content = """[00:20.00]Third
[00:10.00]First
[00:15.00]Second
"""
    lrc_file.write_text(lrc_content, encoding="utf-8")

    parser = LRCParser(lrc_file)
    lyrics = parser.parse_lyrics()

    assert len(lyrics) == 3
    assert lyrics[0].text == "First"
    assert lyrics[1].text == "Second"
    assert lyrics[2].text == "Third"


def test_empty_lrc_file(tmp_path: Path) -> None:
    """Test parsing empty LRC file."""
    lrc_file = tmp_path / "empty.lrc"
    lrc_file.write_text("", encoding="utf-8")

    parser = LRCParser(lrc_file)
    lyrics = parser.parse_lyrics()

    assert len(lyrics) == 0
