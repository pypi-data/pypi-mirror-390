"""Tests for ASS converter."""

from pathlib import Path

import pytest

from ass2lrc.ass_converter import ASSConverter
from ass2lrc.models import LyricLine, Metadata, Syllable


@pytest.fixture
def sample_metadata() -> Metadata:
    """Create sample metadata."""
    return Metadata(
        title="Test Song",
        artist="Test Artist",
        album="Test Album",
    )


@pytest.fixture
def sample_lyrics() -> list[LyricLine]:
    """Create sample lyrics."""
    return [
        LyricLine(
            start_time=10.0,
            text="Simple line",
            syllables=[],
            original_end_time=12.0,
        ),
        LyricLine(
            start_time=15.0,
            text="Enhanced line",
            syllables=[
                Syllable(text="Enhanced ", start_time=15.0, duration=0.5),
                Syllable(text="line", start_time=15.5, duration=0.5),
            ],
            original_end_time=16.0,
        ),
    ]


def test_format_ass_time() -> None:
    """Test ASS timestamp formatting."""
    assert ASSConverter._format_ass_time(0.0) == "0:00:00.00"
    assert ASSConverter._format_ass_time(83.45) == "0:01:23.45"
    assert ASSConverter._format_ass_time(3661.5) == "1:01:01.50"


def test_generate_script_info(sample_metadata: Metadata) -> None:
    """Test Script Info section generation."""
    converter = ASSConverter(metadata=sample_metadata)
    script_info = converter._generate_script_info()

    assert "[Script Info]" in script_info
    assert "Title: Test Song" in script_info
    assert "ScriptType: v4.00+" in script_info
    assert "PlayResX: 640" in script_info


def test_generate_dialogue_line_simple() -> None:
    """Test generating simple dialogue line without karaoke."""
    converter = ASSConverter(with_karaoke=False)
    lyric = LyricLine(
        start_time=10.0,
        text="Simple line",
        syllables=[],
        original_end_time=12.0,
    )

    line = converter._generate_dialogue_line(lyric)

    assert line.startswith("Dialogue: 0,0:00:10.00,0:00:12.00,Default")
    assert line.endswith(",,Simple line")
    assert "\\k" not in line


def test_generate_dialogue_line_with_karaoke() -> None:
    """Test generating dialogue line with karaoke tags."""
    converter = ASSConverter(with_karaoke=True)
    lyric = LyricLine(
        start_time=10.0,
        text="Karaoke line",
        syllables=[
            Syllable(text="Kara", start_time=10.0, duration=0.5),
            Syllable(text="oke ", start_time=10.5, duration=0.3),
            Syllable(text="line", start_time=10.8, duration=0.4),
        ],
        original_end_time=12.0,
    )

    line = converter._generate_dialogue_line(lyric)

    # End time is calculated from syllables (10.0 + 0.5 + 0.3 + 0.4 = 11.2)
    assert "Dialogue: 0,0:00:10.00,0:00:11.20" in line
    assert "{\\k50}Kara" in line
    assert "{\\k30}oke " in line
    assert "{\\k40}line" in line


def test_convert_to_ass_file(
    tmp_path: Path,
    sample_metadata: Metadata,
    sample_lyrics: list[LyricLine],
) -> None:
    """Test converting lyrics to ASS file."""
    output_file = tmp_path / "test.ass"
    converter = ASSConverter(metadata=sample_metadata, with_karaoke=True)
    converter.convert(sample_lyrics, output_file)

    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")

    # Check sections exist
    assert "[Script Info]" in content
    assert "[V4+ Styles]" in content
    assert "[Events]" in content

    # Check metadata
    assert "Title: Test Song" in content

    # Check dialogue lines
    assert "Dialogue: 0,0:00:10.00,0:00:12.00" in content
    assert "Simple line" in content
    assert "{\\k50}Enhanced {\\k50}line" in content


def test_convert_without_karaoke(
    tmp_path: Path,
    sample_lyrics: list[LyricLine],
) -> None:
    """Test converting without karaoke tags."""
    output_file = tmp_path / "test_no_karaoke.ass"
    converter = ASSConverter(with_karaoke=False)
    converter.convert(sample_lyrics, output_file)

    content = output_file.read_text(encoding="utf-8")

    # Should not contain karaoke tags
    assert "\\k" not in content
    assert "Enhanced line" in content


def test_ass_file_structure(tmp_path: Path, sample_lyrics: list[LyricLine]) -> None:
    """Test ASS file has proper structure with correct spacing."""
    output_file = tmp_path / "test_structure.ass"
    converter = ASSConverter()
    converter.convert(sample_lyrics, output_file)

    content = output_file.read_text(encoding="utf-8")
    lines = content.split("\n")

    # Check for proper section separation
    styles_idx = next(i for i, line in enumerate(lines) if "[V4+ Styles]" in line)
    events_idx = next(i for i, line in enumerate(lines) if "[Events]" in line)

    # Should have blank lines between sections
    assert lines[styles_idx - 1] == ""
    assert lines[events_idx - 1] == ""


def test_default_metadata_title() -> None:
    """Test default title when no metadata provided."""
    converter = ASSConverter()
    script_info = converter._generate_script_info()

    assert "Title: Default Aegisub file" in script_info
