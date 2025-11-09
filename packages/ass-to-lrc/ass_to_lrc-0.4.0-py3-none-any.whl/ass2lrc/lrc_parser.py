"""LRC file parser."""

import re
from pathlib import Path

from .models import LyricLine, Metadata, Syllable


class LRCParser:
    """Parser for LRC lyrics files."""

    def __init__(self, file_path: Path, include_comments: bool = False):
        """Initialize parser with LRC file path."""
        self.file_path = file_path
        self.include_comments = include_comments
        self.metadata = Metadata()
        self.lines: list[str] = []
        self._load_file()
        self._parse_all_metadata()

    def _load_file(self) -> None:
        """Load and read the LRC file."""
        with open(self.file_path, encoding="utf-8") as f:
            self.lines = [line.rstrip() for line in f.readlines()]

    def _parse_all_metadata(self) -> None:
        """Parse all metadata tags from the file."""
        for line in self.lines:
            self._parse_metadata(line.strip())

    def _parse_timestamp(self, timestamp: str) -> float:
        """Parse LRC timestamp [mm:ss.xx] or <mm:ss.xx> to seconds."""
        timestamp = timestamp.strip("[]<>")
        match = re.match(r"(\d+):(\d+\.\d+)", timestamp)
        if not match:
            return 0.0
        minutes = int(match.group(1))
        seconds = float(match.group(2))
        return minutes * 60 + seconds

    def _parse_metadata(self, line: str) -> bool:
        """Parse metadata tag and return True if it was metadata."""
        # Match metadata tags like [ti:Title]
        match = re.match(r"\[([^:\]]+):([^\]]*)\]", line)
        if not match:
            return False

        tag = match.group(1).lower()
        value = match.group(2)

        if tag == "ti":
            self.metadata.title = value
        elif tag == "ar":
            self.metadata.artist = value
        elif tag == "al":
            self.metadata.album = value
        elif tag == "au":
            self.metadata.author = value
        elif tag == "lr":
            self.metadata.lyricist = value
        elif tag == "length":
            self.metadata.length = value
        elif tag == "by":
            self.metadata.by = value
        elif tag == "offset":
            self.metadata.offset = value
        elif tag == "re":
            self.metadata.tool = value
        elif tag == "ve":
            self.metadata.version = value
        elif tag == "#":
            if self.metadata.comments is not None:
                self.metadata.comments.append(value)
        else:
            return False

        return True

    def _parse_enhanced_line(self, timestamp: float, text: str) -> LyricLine:
        """Parse enhanced LRC with inline timestamps."""
        syllables: list[Syllable] = []

        # Pattern to match inline timestamps and text between them
        pattern = r"<(\d+:\d+\.\d+)>([^<]*)"
        matches = re.finditer(pattern, text)

        for match in matches:
            inline_time = self._parse_timestamp(match.group(1))
            content = match.group(2)

            if syllables:
                # Calculate duration for previous syllable
                syllables[-1].duration = inline_time - syllables[-1].start_time

            if content:
                syllables.append(Syllable(text=content, start_time=inline_time, duration=0))

        # Clean text for plain display
        plain_text = re.sub(r"<\d+:\d+\.\d+>", "", text)

        return LyricLine(
            start_time=timestamp,
            text=plain_text,
            syllables=syllables,
        )

    def parse_lyrics(self) -> list[LyricLine]:
        """Parse all lyric lines from LRC file."""
        lyrics = []
        empty_timestamps = []

        for line in self.lines:
            line = line.strip()
            if not line:
                continue

            # Try to parse as metadata first
            if self._parse_metadata(line):
                continue

            # Check if this is a comment line (no timestamp) [#]text
            if line.startswith("[#]"):
                if self.include_comments:
                    text = line[3:]  # Remove [#] prefix
                    lyrics.append(
                        LyricLine(
                            start_time=0.0,  # Use 0.0 for comment lines
                            text=text,
                            syllables=[],
                            is_comment=True,
                        )
                    )
                continue

            # Match timestamp(s) and text
            # Pattern for [mm:ss.xx]text or [mm:ss.xx]
            match = re.match(r"(\[[\d:\.]+\])(.*)$", line)
            if not match:
                continue

            timestamp_str = match.group(1)
            text = match.group(2)

            # Parse the timestamp
            timestamp = self._parse_timestamp(timestamp_str)

            # Collect empty lines (just timestamps) for end time calculation
            if not text:
                empty_timestamps.append(timestamp)
                continue

            # Check if enhanced LRC (has inline timestamps)
            if "<" in text and ">" in text:
                lyric = self._parse_enhanced_line(timestamp, text.strip())
                lyrics.append(lyric)
            else:
                # Simple LRC
                lyrics.append(
                    LyricLine(
                        start_time=timestamp,
                        text=text.strip(),
                        syllables=[],
                    )
                )

        # Sort lyrics and post-process to set end times
        lyrics = sorted(lyrics, key=lambda x: x.start_time)
        self._calculate_end_times(lyrics, empty_timestamps)
        return lyrics

    def _calculate_end_times(self, lyrics: list[LyricLine], empty_timestamps: list[float]) -> None:
        """Calculate end times for lyrics based on next line's start time."""
        for i, lyric in enumerate(lyrics):
            # If line has syllables with timing
            if lyric.syllables and lyric.syllables[-1].duration == 0:
                # Determine the end time for the last syllable
                if i < len(lyrics) - 1:
                    # Use the start time of the next line
                    next_start = lyrics[i + 1].start_time
                    lyric.syllables[-1].duration = next_start - lyric.syllables[-1].start_time
                else:
                    # For the last line, check if there's an empty timestamp marker
                    later_timestamps = [t for t in empty_timestamps if t > lyric.start_time]
                    if later_timestamps:
                        end_time = min(later_timestamps)
                        lyric.syllables[-1].duration = end_time - lyric.syllables[-1].start_time
                    else:
                        # Default: use a reasonable duration (e.g., 2 seconds)
                        lyric.syllables[-1].duration = 2.0

    def has_enhanced_timing(self) -> bool:
        """Check if any lyrics have enhanced inline timing."""
        lyrics = self.parse_lyrics()
        return any(lyric.syllables for lyric in lyrics)
