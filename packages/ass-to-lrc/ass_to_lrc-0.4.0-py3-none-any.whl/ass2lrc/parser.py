"""ASS file parser."""

import re
from pathlib import Path

import ass

from .models import LyricLine, Metadata, Syllable


class ASSParser:
    """Parser for ASS subtitle files."""

    def __init__(self, file_path: Path, include_comments: bool = False):
        """Initialize parser with ASS file path."""
        self.file_path = file_path
        self.include_comments = include_comments
        with open(file_path, encoding="utf-8-sig") as f:
            self.doc = ass.parse(f)
        self.metadata = Metadata()
        self._parse_metadata()

    def _parse_metadata(self) -> None:
        """Extract metadata from ASS file."""
        for event in self.doc.events:
            # Check for metadata tags in Comment events or effect field
            is_comment_event = type(event).__name__ == "Comment"
            is_tag_effect = event.effect == "tag"

            if is_comment_event or is_tag_effect:
                name_lower = event.name.lower()
                text = event.text

                if name_lower == "ti":
                    self.metadata.title = text
                elif name_lower == "ar":
                    self.metadata.artist = text
                elif name_lower == "al":
                    self.metadata.album = text
                elif name_lower == "au":
                    self.metadata.author = text
                elif name_lower == "lr":
                    self.metadata.lyricist = text
                elif name_lower == "length":
                    self.metadata.length = text
                elif name_lower == "by":
                    self.metadata.by = text
                elif name_lower == "offset":
                    self.metadata.offset = text
                elif name_lower in ("re", "tool"):
                    self.metadata.tool = text
                elif name_lower == "ve":
                    self.metadata.version = text
                elif name_lower == "#":
                    if self.metadata.comments is not None:
                        self.metadata.comments.append(text)

    def _parse_karaoke_tags(self, text: str, start_time: float) -> list[Syllable]:
        """Parse karaoke timing tags from ASS text."""
        syllables = []
        current_time = start_time

        # Remove override blocks but keep karaoke tags
        pattern = r"\{([^}]*)\}([^{]*)"
        matches = re.finditer(pattern, text)

        for match in matches:
            tags = match.group(1)
            content = match.group(2)

            # Extract \K or \k duration (centiseconds)
            k_match = re.search(r"\\[Kk](\d+)", tags)
            if k_match:
                duration_cs = int(k_match.group(1))
                duration_s = duration_cs / 100.0

                if content:  # Only add non-empty syllables
                    syllables.append(
                        Syllable(text=content, start_time=current_time, duration=duration_s)
                    )
                current_time += duration_s

        # Handle any remaining text without tags
        remaining = re.sub(r"\{[^}]*\}", "", text)
        if remaining and not syllables:
            syllables.append(Syllable(text=remaining, start_time=start_time, duration=0))

        return syllables

    def parse_lyrics(self) -> list[LyricLine]:
        """Parse all lyric lines from ASS file."""
        lyrics = []

        for event in self.doc.events:
            # Check if this is a Comment event
            is_comment_event = type(event).__name__ == "Comment"

            # Skip metadata tag lines
            if event.effect == "tag":
                continue

            # Skip Comment events unless include_comments is enabled
            if is_comment_event and not self.include_comments:
                continue

            # Convert time to seconds
            start_time = event.start.total_seconds()
            end_time = event.end.total_seconds()

            # Parse karaoke tags
            syllables = self._parse_karaoke_tags(event.text, start_time)

            # Clean text for plain display
            plain_text = re.sub(r"\{[^}]*\}", "", event.text)

            lyrics.append(
                LyricLine(
                    start_time=start_time,
                    text=plain_text,
                    syllables=syllables,
                    style=event.style,
                    name=event.name,
                    effect=event.effect,
                    original_end_time=end_time,
                    is_comment=is_comment_event,
                )
            )

        return sorted(lyrics, key=lambda x: x.start_time)

    def has_karaoke_timing(self) -> bool:
        """Check if any lyrics have karaoke timing."""
        lyrics = self.parse_lyrics()
        return any(
            lyric.syllables and any(syll.duration > 0 for syll in lyric.syllables)
            for lyric in lyrics
        )
