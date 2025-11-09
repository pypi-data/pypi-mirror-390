"""Tests for ASS parser."""

from pathlib import Path

import pytest

from ass2lrc.parser import ASSParser


@pytest.fixture
def sample_ass_file(tmp_path: Path) -> Path:
    """Create a sample ASS file for testing."""
    ass_content = """[Script Info]
Title: Test Song
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,40,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,1,0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Comment: 0,0:00:00.00,0:00:00.00,Default,ti,0,0,0,,Test Title
Comment: 0,0:00:00.00,0:00:00.00,Default,ar,0,0,0,,Test Artist
Comment: 0,0:00:00.00,0:00:00.00,Default,#,0,0,0,,This is a comment
Dialogue: 0,0:00:10.00,0:00:15.00,Default,,0,0,0,,{\\K50}Test{\\K50}lyrics{\\K50}here
Dialogue: 0,0:00:16.00,0:00:20.00,Default,,0,0,0,,Plain lyrics without timing
"""  # noqa: E501
    file_path = tmp_path / "test.ass"
    file_path.write_text(ass_content, encoding="utf-8")
    return file_path


@pytest.fixture
def tag_effect_ass_file(tmp_path: Path) -> Path:
    """Create an ASS file with tag effect metadata."""
    ass_content = """[Script Info]
Title: Test Song
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,40,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,1,0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:02.00,Default,lr,0,0,0,tag,Test Lyricist
Dialogue: 0,0:00:10.00,0:00:15.00,Default,,0,0,0,,Test lyrics
"""  # noqa: E501
    file_path = tmp_path / "test_tag.ass"
    file_path.write_text(ass_content, encoding="utf-8")
    return file_path


def test_parser_initialization(sample_ass_file: Path) -> None:
    """Test parser initialization."""
    parser = ASSParser(sample_ass_file)
    assert parser.file_path == sample_ass_file
    assert parser.metadata is not None


def test_parse_comment_metadata(sample_ass_file: Path) -> None:
    """Test parsing metadata from Comment events."""
    parser = ASSParser(sample_ass_file)
    assert parser.metadata.title == "Test Title"
    assert parser.metadata.artist == "Test Artist"
    assert parser.metadata.comments is not None
    assert "This is a comment" in parser.metadata.comments


def test_parse_tag_effect_metadata(tag_effect_ass_file: Path) -> None:
    """Test parsing metadata from effect=tag."""
    parser = ASSParser(tag_effect_ass_file)
    assert parser.metadata.lyricist == "Test Lyricist"


def test_parse_lyrics(sample_ass_file: Path) -> None:
    """Test parsing lyrics from ASS file."""
    parser = ASSParser(sample_ass_file)
    lyrics = parser.parse_lyrics()

    assert len(lyrics) == 2
    assert lyrics[0].start_time == 10.0
    assert lyrics[1].start_time == 16.0


def test_parse_karaoke_tags(sample_ass_file: Path) -> None:
    """Test parsing karaoke timing tags."""
    parser = ASSParser(sample_ass_file)
    lyrics = parser.parse_lyrics()

    # First line has karaoke tags
    first_line = lyrics[0]
    assert len(first_line.syllables) == 3
    assert first_line.syllables[0].text == "Test"
    assert first_line.syllables[0].duration == 0.5
    assert first_line.syllables[1].text == "lyrics"
    assert first_line.syllables[2].text == "here"


def test_parse_plain_text(sample_ass_file: Path) -> None:
    """Test parsing plain text without karaoke tags."""
    parser = ASSParser(sample_ass_file)
    lyrics = parser.parse_lyrics()

    # Second line has no karaoke tags
    second_line = lyrics[1]
    assert second_line.text == "Plain lyrics without timing"
    assert len(second_line.syllables) == 1


def test_lyrics_sorted_by_time(sample_ass_file: Path) -> None:
    """Test that lyrics are sorted by start time."""
    parser = ASSParser(sample_ass_file)
    lyrics = parser.parse_lyrics()

    for i in range(len(lyrics) - 1):
        assert lyrics[i].start_time <= lyrics[i + 1].start_time


def test_skip_comment_events(sample_ass_file: Path) -> None:
    """Test that Comment events are not included in lyrics."""
    parser = ASSParser(sample_ass_file)
    lyrics = parser.parse_lyrics()

    # Only Dialogue events should be in lyrics, not Comments
    assert all(lyric.text not in ["Test Title", "Test Artist"] for lyric in lyrics)
