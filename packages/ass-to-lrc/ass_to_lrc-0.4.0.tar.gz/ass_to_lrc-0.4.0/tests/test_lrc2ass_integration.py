"""Integration tests for LRC to ASS conversion."""

from pathlib import Path

import pytest

from ass2lrc.ass_converter import ASSConverter
from ass2lrc.lrc_parser import LRCParser


@pytest.fixture
def sample_lrc_path() -> Path:
    """Get path to sample LRC file."""
    return Path(__file__).parent / "test_lrc_sample.lrc"


def test_full_lrc_to_ass_workflow(tmp_path: Path, sample_lrc_path: Path) -> None:
    """Test complete LRC to ASS conversion workflow."""
    # Parse LRC
    parser = LRCParser(sample_lrc_path)
    lyrics = parser.parse_lyrics()

    assert len(lyrics) == 4  # Empty lines are skipped
    assert parser.metadata.title == "Sample Enhanced Song"
    assert parser.metadata.artist == "Test Artist"

    # Convert to ASS with karaoke
    output_file = tmp_path / "output.ass"
    converter = ASSConverter(metadata=parser.metadata, with_karaoke=True)
    converter.convert(lyrics, output_file)

    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")

    # Verify structure
    assert "[Script Info]" in content
    assert "[V4+ Styles]" in content
    assert "[Events]" in content

    # Verify metadata
    assert "Title: Sample Enhanced Song" in content

    # Verify karaoke tags for enhanced lines
    assert "\\k50" in content  # "This" duration
    assert "\\k30" in content  # "is" duration

    # Verify simple lines
    assert "Simple line without timing" in content


def test_lrc_to_ass_without_karaoke(tmp_path: Path, sample_lrc_path: Path) -> None:
    """Test LRC to ASS conversion without karaoke tags."""
    parser = LRCParser(sample_lrc_path)
    lyrics = parser.parse_lyrics()

    output_file = tmp_path / "output_no_karaoke.ass"
    converter = ASSConverter(metadata=parser.metadata, with_karaoke=False)
    converter.convert(lyrics, output_file)

    content = output_file.read_text(encoding="utf-8")

    # Should not have karaoke tags
    assert "\\k" not in content

    # Should have plain text
    assert "This is enhanced LRC" in content
    assert "Word by word timing" in content


def test_roundtrip_preservation(tmp_path: Path) -> None:
    """Test that basic data is preserved in LRC->ASS conversion."""
    # Create a simple LRC
    lrc_file = tmp_path / "test.lrc"
    lrc_content = """[ti:Roundtrip Test]
[ar:Test Artist]
[00:10.50]First line
[00:15.00]<00:15.00>En<00:15.20>han<00:15.40>ced
"""
    lrc_file.write_text(lrc_content, encoding="utf-8")

    # Parse and convert
    parser = LRCParser(lrc_file)
    lyrics = parser.parse_lyrics()

    assert len(lyrics) == 2
    assert lyrics[0].start_time == 10.5
    assert lyrics[1].syllables[0].duration == pytest.approx(0.2)

    # Convert to ASS
    output_file = tmp_path / "output.ass"
    converter = ASSConverter(metadata=parser.metadata, with_karaoke=True)
    converter.convert(lyrics, output_file)

    content = output_file.read_text(encoding="utf-8")

    # Check timing preserved
    assert "0:00:10.50" in content
    assert "0:00:15.00" in content

    # Check karaoke timing (20 centiseconds)
    assert "\\k20" in content


def test_simple_lrc_to_ass(tmp_path: Path) -> None:
    """Test converting simple LRC without any enhanced timing."""
    lrc_file = tmp_path / "simple.lrc"
    lrc_content = """[ti:Simple Song]
[00:05.00]Line one
[00:10.00]Line two
[00:15.00]Line three
"""
    lrc_file.write_text(lrc_content, encoding="utf-8")

    parser = LRCParser(lrc_file)
    lyrics = parser.parse_lyrics()

    assert parser.has_enhanced_timing() is False

    output_file = tmp_path / "simple.ass"
    converter = ASSConverter(metadata=parser.metadata, with_karaoke=False)
    converter.convert(lyrics, output_file)

    content = output_file.read_text(encoding="utf-8")

    assert "Line one" in content
    assert "Line two" in content
    assert "Line three" in content
    assert "\\k" not in content
