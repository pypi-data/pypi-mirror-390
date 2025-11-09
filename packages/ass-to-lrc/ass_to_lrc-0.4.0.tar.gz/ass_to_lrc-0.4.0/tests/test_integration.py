"""Integration tests for full workflow."""

from pathlib import Path

import pytest

from ass2lrc.converter import LRCConverter
from ass2lrc.expander import LRCExpander
from ass2lrc.parser import ASSParser


@pytest.fixture
def full_ass_file(tmp_path: Path) -> Path:
    """Create a complete ASS file for integration testing."""
    # fmt: off
    content = """[Script Info]
Title: Integration Test
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,40,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,1,0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Comment: 0,0:00:00.00,0:00:00.00,Default,ti,0,0,0,,Integration Test Song
Comment: 0,0:00:00.00,0:00:00.00,Default,ar,0,0,0,,Test Artist
Comment: 0,0:00:00.00,0:00:00.00,Default,lr,0,0,0,,Test Lyricist
Dialogue: 0,0:00:10.00,0:00:15.00,Default,,0,0,0,,{\\K50}First{\\K50}line
Dialogue: 0,0:00:16.00,0:00:20.00,Default,,0,0,0,,{\\K40}Second{\\K40}line
Dialogue: 0,0:00:30.00,0:00:35.00,Default,,0,0,0,,{\\K50}First{\\K50}line
""" # noqa: E501
    # fmt: on
    file_path = tmp_path / "integration.ass"
    file_path.write_text(content, encoding="utf-8")
    return file_path


def test_full_enhanced_workflow(full_ass_file: Path, tmp_path: Path) -> None:
    """Test complete workflow: ASS → Enhanced LRC."""
    output_file = tmp_path / "output.elrc"

    # Parse
    parser = ASSParser(full_ass_file)
    lyrics = parser.parse_lyrics()

    # Convert
    converter = LRCConverter(
        metadata=parser.metadata,
        enhanced=True,
        line_gap=1.0,
    )
    converter.convert(lyrics, output_file)

    # Verify
    content = output_file.read_text(encoding="utf-8")
    assert "[ti:Integration Test Song]" in content
    assert "[ar:Test Artist]" in content
    assert "[lr:Test Lyricist]" in content
    assert "<00:10.00>" in content  # Enhanced timing
    assert "First" in content
    assert "line" in content


def test_full_simple_workflow(full_ass_file: Path, tmp_path: Path) -> None:
    """Test complete workflow: ASS → Simple LRC."""
    output_file = tmp_path / "output.lrc"

    # Parse
    parser = ASSParser(full_ass_file)
    lyrics = parser.parse_lyrics()

    # Convert
    converter = LRCConverter(
        metadata=parser.metadata,
        enhanced=False,
        line_gap=1.0,
    )
    converter.convert(lyrics, output_file)

    # Verify
    content = output_file.read_text(encoding="utf-8")
    assert "[ti:Integration Test Song]" in content
    assert "<00:10.00>" not in content  # No enhanced timing
    assert "Firstline" in content


def test_compact_and_expand_workflow(full_ass_file: Path, tmp_path: Path) -> None:
    """Test workflow: ASS → Compact LRC → Expanded LRC."""
    compact_file = tmp_path / "compact.lrc"
    expanded_file = tmp_path / "expanded.lrc"

    # Parse and convert to compact
    parser = ASSParser(full_ass_file)
    lyrics = parser.parse_lyrics()
    converter = LRCConverter(
        metadata=parser.metadata,
        enhanced=False,
        line_gap=0.0,
        compact=True,
    )
    converter.convert(lyrics, compact_file)

    # Verify compact format
    compact_content = compact_file.read_text(encoding="utf-8")
    assert "[00:10.00][00:30.00]Firstline" in compact_content

    # Expand
    expander = LRCExpander()
    expander.expand(compact_file, expanded_file)

    # Verify expanded format
    expanded_content = expanded_file.read_text(encoding="utf-8")
    assert "[00:10.00]Firstline" in expanded_content
    assert "[00:30.00]Firstline" in expanded_content


def test_metadata_preservation(full_ass_file: Path, tmp_path: Path) -> None:
    """Test that metadata is preserved through conversion."""
    output_file = tmp_path / "metadata_test.lrc"

    parser = ASSParser(full_ass_file)
    converter = LRCConverter(metadata=parser.metadata, enhanced=False, line_gap=0.0)
    lyrics = parser.parse_lyrics()
    converter.convert(lyrics, output_file)

    content = output_file.read_text(encoding="utf-8")

    # All metadata should be present
    assert "[ti:Integration Test Song]" in content
    assert "[ar:Test Artist]" in content
    assert "[lr:Test Lyricist]" in content


def test_multiple_conversions(full_ass_file: Path, tmp_path: Path) -> None:
    """Test multiple conversions from same source."""
    parser = ASSParser(full_ass_file)
    lyrics = parser.parse_lyrics()

    # Enhanced
    enhanced_file = tmp_path / "enhanced.elrc"
    converter_enhanced = LRCConverter(metadata=parser.metadata, enhanced=True, line_gap=1.0)
    converter_enhanced.convert(lyrics, enhanced_file)

    # Simple
    simple_file = tmp_path / "simple.lrc"
    converter_simple = LRCConverter(metadata=parser.metadata, enhanced=False, line_gap=1.0)
    converter_simple.convert(lyrics, simple_file)

    # Compact
    compact_file = tmp_path / "compact.lrc"
    converter_compact = LRCConverter(
        metadata=parser.metadata, enhanced=False, line_gap=0.0, compact=True
    )
    converter_compact.convert(lyrics, compact_file)

    # All should exist and have content
    assert enhanced_file.exists()
    assert simple_file.exists()
    assert compact_file.exists()

    # All should have metadata
    for file in [enhanced_file, simple_file, compact_file]:
        content = file.read_text(encoding="utf-8")
        assert "[ti:Integration Test Song]" in content


def test_normal_sample_without_karaoke(tmp_path: Path) -> None:
    """Test conversion of ASS file without karaoke timing."""
    normal_sample = Path(__file__).parent / "test_normal_sample.ass"
    output_file = tmp_path / "normal_output.lrc"

    # Parse
    parser = ASSParser(normal_sample)
    lyrics = parser.parse_lyrics()

    # Should have lyrics
    assert len(lyrics) > 0

    # Should not have karaoke timing
    assert not parser.has_karaoke_timing()

    # Convert to simple LRC
    converter = LRCConverter(
        metadata=parser.metadata,
        enhanced=False,
        line_gap=1.0,
    )
    converter.convert(lyrics, output_file)

    # Verify
    content = output_file.read_text(encoding="utf-8")
    assert "[00:46.07]" in content
    assert "نار في نار عم تولع حْوَالينا" in content
    assert "<" not in content  # No enhanced timing tags
