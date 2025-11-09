"""Tests for LRC expander."""

from pathlib import Path

import pytest

from ass2lrc.expander import LRCExpander


@pytest.fixture
def compact_lrc_file(tmp_path: Path) -> Path:
    """Create a compact LRC file for testing."""
    content = """[ti:Test Song]
[ar:Test Artist]
[00:10.00][00:30.00][00:50.00]Chorus line
[00:15.00]Verse one
[00:35.00]Verse two
"""
    file_path = tmp_path / "compact.lrc"
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def simple_lrc_file(tmp_path: Path) -> Path:
    """Create a simple LRC file."""
    content = """[ti:Test Song]
[00:10.00]First line
[00:15.00]Second line
"""
    file_path = tmp_path / "simple.lrc"
    file_path.write_text(content, encoding="utf-8")
    return file_path


def test_extract_timestamps() -> None:
    """Test timestamp extraction."""
    expander = LRCExpander()
    timestamps, content = expander._extract_timestamps("[00:10.00][00:20.00]Test lyrics")

    assert len(timestamps) == 2
    assert timestamps[0] == 10.0
    assert timestamps[1] == 20.0
    assert content == "Test lyrics"


def test_extract_single_timestamp() -> None:
    """Test single timestamp extraction."""
    expander = LRCExpander()
    timestamps, content = expander._extract_timestamps("[00:10.50]Test line")

    assert len(timestamps) == 1
    assert timestamps[0] == 10.5
    assert content == "Test line"


def test_expand_compact_lrc(compact_lrc_file: Path, tmp_path: Path) -> None:
    """Test expanding compact LRC format."""
    output_file = tmp_path / "expanded.lrc"
    expander = LRCExpander()
    expander.expand(compact_lrc_file, output_file)

    content = output_file.read_text(encoding="utf-8")

    # Check metadata is preserved
    assert "[ti:Test Song]" in content
    assert "[ar:Test Artist]" in content

    # Check that chorus appears three times
    assert content.count("Chorus line") == 3

    # Check individual timestamps
    assert "[00:10.00]Chorus line" in content
    assert "[00:30.00]Chorus line" in content
    assert "[00:50.00]Chorus line" in content


def test_expand_already_standard(simple_lrc_file: Path, tmp_path: Path) -> None:
    """Test expanding already standard format doesn't break."""
    output_file = tmp_path / "still_standard.lrc"
    expander = LRCExpander()
    expander.expand(simple_lrc_file, output_file)

    content = output_file.read_text(encoding="utf-8")

    # Should still work correctly
    assert "[ti:Test Song]" in content
    assert "[00:10.00]First line" in content
    assert "[00:15.00]Second line" in content


def test_sorted_output(compact_lrc_file: Path, tmp_path: Path) -> None:
    """Test that expanded output is sorted by timestamp."""
    output_file = tmp_path / "sorted.lrc"
    expander = LRCExpander()
    expander.expand(compact_lrc_file, output_file)

    content = output_file.read_text(encoding="utf-8")
    lines = [line for line in content.split("\n") if line.startswith("[00:")]

    # Extract timestamps and check order
    timestamps = []
    for line in lines:
        time_str = line.split("]")[0][1:]
        minutes, seconds = time_str.split(":")
        total_seconds = int(minutes) * 60 + float(seconds)
        timestamps.append(total_seconds)

    assert timestamps == sorted(timestamps)


def test_empty_file(tmp_path: Path) -> None:
    """Test handling empty file."""
    empty_file = tmp_path / "empty.lrc"
    empty_file.write_text("", encoding="utf-8")

    output_file = tmp_path / "expanded_empty.lrc"
    expander = LRCExpander()
    expander.expand(empty_file, output_file)

    content = output_file.read_text(encoding="utf-8")
    assert content.strip() == ""


def test_metadata_only_file(tmp_path: Path) -> None:
    """Test file with only metadata."""
    metadata_file = tmp_path / "metadata.lrc"
    metadata_file.write_text("[ti:Test]\n[ar:Artist]\n", encoding="utf-8")

    output_file = tmp_path / "expanded_metadata.lrc"
    expander = LRCExpander()
    expander.expand(metadata_file, output_file)

    content = output_file.read_text(encoding="utf-8")
    assert "[ti:Test]" in content
    assert "[ar:Artist]" in content
