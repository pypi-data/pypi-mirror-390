"""Tests for effect-based line break feature."""

from pathlib import Path

import pytest

from ass2lrc.converter import LRCConverter
from ass2lrc.models import LyricLine


@pytest.fixture
def lyrics_with_break_effect() -> list[LyricLine]:
    """Create sample lyrics with break effect."""
    return [
        LyricLine(
            start_time=10.0,
            text="First line",
            syllables=[],
            effect="",
            original_end_time=12.0,
        ),
        LyricLine(
            start_time=15.0,
            text="Second line with break",
            syllables=[],
            effect="linebreak",
            original_end_time=17.0,
        ),
        LyricLine(
            start_time=20.0,
            text="Third line",
            syllables=[],
            effect="",
            original_end_time=22.0,
        ),
    ]


def test_effect_linebreak_in_lrc(
    tmp_path: Path,
    lyrics_with_break_effect: list[LyricLine],
) -> None:
    """Test that effect containing 'break' adds empty line."""
    output_file = tmp_path / "test_break.lrc"
    converter = LRCConverter(enhanced=False)
    converter.convert(lyrics_with_break_effect, output_file)

    content = output_file.read_text(encoding="utf-8")
    lines = content.strip().split("\n")

    # Find the line with break effect
    break_line_idx = next(i for i, line in enumerate(lines) if "Second line with break" in line)

    # Next line should be empty timestamped line
    assert lines[break_line_idx + 1] == "[00:17.00]"


def test_effect_linebreak_case_insensitive(tmp_path: Path) -> None:
    """Test that break detection is case-insensitive."""
    lyrics = [
        LyricLine(
            start_time=10.0,
            text="Line with BREAK",
            syllables=[],
            effect="LINEBREAK",
            original_end_time=12.0,
        ),
        LyricLine(
            start_time=15.0,
            text="Line with Break",
            syllables=[],
            effect="ChorusBreak",
            original_end_time=17.0,
        ),
        LyricLine(
            start_time=20.0,
            text="Normal line",
            syllables=[],
            effect="",
            original_end_time=22.0,
        ),
    ]

    output_file = tmp_path / "test_case.lrc"
    converter = LRCConverter(enhanced=False)
    converter.convert(lyrics, output_file)

    content = output_file.read_text(encoding="utf-8")

    # Should have two empty lines after the break effects
    assert content.count("[00:12.00]") == 1
    assert content.count("[00:17.00]") == 1


def test_effect_no_break_no_empty_line(tmp_path: Path) -> None:
    """Test that lines without break effect don't add empty lines."""
    lyrics = [
        LyricLine(
            start_time=10.0,
            text="First line",
            syllables=[],
            effect="",
            original_end_time=12.0,
        ),
        LyricLine(
            start_time=15.0,
            text="Second line",
            syllables=[],
            effect="normal",
            original_end_time=17.0,
        ),
    ]

    output_file = tmp_path / "test_no_break.lrc"
    converter = LRCConverter(enhanced=False, line_gap=0)
    converter.convert(lyrics, output_file)

    content = output_file.read_text(encoding="utf-8")
    lines = [line for line in content.strip().split("\n") if line]

    # Should only have the two lyrics plus final empty line
    # No additional empty lines between them
    assert len(lines) == 3  # 2 lyrics + 1 final empty


def test_effect_break_vs_gap_priority(tmp_path: Path) -> None:
    """Test that break effect takes priority over gap detection."""
    lyrics = [
        LyricLine(
            start_time=10.0,
            text="First line",
            syllables=[],
            effect="break",
            original_end_time=12.0,
        ),
        LyricLine(
            start_time=20.0,
            text="Second line",
            syllables=[],
            effect="",
            original_end_time=22.0,
        ),
    ]

    output_file = tmp_path / "test_priority.lrc"
    converter = LRCConverter(enhanced=False, line_gap=1.0)
    converter.convert(lyrics, output_file)

    content = output_file.read_text(encoding="utf-8")

    # Should have break line at end_time of first line
    assert "[00:12.00]" in content

    # Should not have gap line because elif prevents it
    lines = content.strip().split("\n")
    timestamp_lines = [line for line in lines if line.startswith("[")]

    # First line, break line, second line, final empty line = 4
    assert len(timestamp_lines) == 4


def test_effect_break_with_enhanced_lrc(tmp_path: Path) -> None:
    """Test that break effect works with enhanced LRC format."""
    from ass2lrc.models import Syllable

    lyrics = [
        LyricLine(
            start_time=10.0,
            text="Enhanced line",
            syllables=[
                Syllable(text="En", start_time=10.0, duration=0.3),
                Syllable(text="han", start_time=10.3, duration=0.3),
                Syllable(text="ced ", start_time=10.6, duration=0.3),
                Syllable(text="line", start_time=10.9, duration=0.3),
            ],
            effect="break",
            original_end_time=12.0,
        ),
        LyricLine(
            start_time=15.0,
            text="Next line",
            syllables=[],
            effect="",
            original_end_time=17.0,
        ),
    ]

    output_file = tmp_path / "test_enhanced_break.lrc"
    converter = LRCConverter(enhanced=True, line_gap=0)
    converter.convert(lyrics, output_file)

    content = output_file.read_text(encoding="utf-8")

    # Should have enhanced line with break
    assert "<00:10.00>" in content
    assert "[00:11.20]" in content  # Break line at end of enhanced line
