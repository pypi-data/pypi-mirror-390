"""LRC file generator."""

import logging
from pathlib import Path

from .models import LyricLine, Metadata

logger = logging.getLogger(__name__)


class LRCConverter:
    """Converter for generating LRC files from parsed lyrics."""

    def __init__(
        self,
        metadata: Metadata | None = None,
        enhanced: bool = True,
        line_gap: float = 1.0,
        compact: bool = False,
        include_comments: bool = False,
    ):
        """
        Initialize LRC converter.

        Args:
            metadata: Metadata to include in LRC file
            enhanced: Whether to generate enhanced LRC with word timing
            line_gap: Gap in seconds to add between lines
            compact: Whether to use compact format (multiple timestamps per line)
            include_comments: Whether to include comment lines
        """
        self.metadata = metadata or Metadata()
        self.enhanced = enhanced
        self.line_gap = line_gap
        self.compact = compact
        self.include_comments = include_comments

        # Disable enhanced timing if compact mode is used
        if self.compact and self.enhanced:
            self.enhanced = False

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """Format seconds as LRC timestamp [mm:ss.xx]."""
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"[{minutes:02d}:{secs:05.2f}]"

    @staticmethod
    def _format_inline_timestamp(seconds: float) -> str:
        """Format seconds as inline timestamp <mm:ss.xx>."""
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"<{minutes:02d}:{secs:05.2f}>"

    def _generate_metadata_tags(self) -> list[str]:
        """Generate metadata tags for LRC file."""
        tags = []

        # Order matters: follow Wikipedia order
        tag_mapping = [
            ("ti", self.metadata.title),
            ("ar", self.metadata.artist),
            ("al", self.metadata.album),
            ("au", self.metadata.author),
            ("lr", self.metadata.lyricist),
            ("length", self.metadata.length),
            ("by", self.metadata.by),
            ("offset", self.metadata.offset),
            ("re", self.metadata.tool),
            ("ve", self.metadata.version),
        ]

        for tag, value in tag_mapping:
            if value is not None:
                tags.append(f"[{tag}:{value}]")

        # Add comments at the end
        if self.metadata.comments is not None:
            for comment in self.metadata.comments:
                tags.append(f"[#]{comment}")

        return tags

    def _generate_line(self, lyric: LyricLine) -> str | None:
        """Generate a single LRC line with optional enhanced timing."""
        # Skip comment lines if not including comments
        if lyric.is_comment and not self.include_comments:
            return None

        # Handle comment lines (no timestamp in LRC)
        if lyric.is_comment:
            return f"[#]{lyric.text}"

        timestamp = self._format_timestamp(lyric.start_time)

        if not self.enhanced or not lyric.syllables:
            return f"{timestamp}{lyric.text}"

        # Enhanced LRC with word timing
        enhanced_text = self._format_inline_timestamp(lyric.start_time)

        for i, syllable in enumerate(lyric.syllables):
            enhanced_text += syllable.text
            # Add timestamp after syllable, except for the last one
            if syllable.text and i < len(lyric.syllables) - 1:
                enhanced_text += self._format_inline_timestamp(syllable.end_time)

        return f"{timestamp}{enhanced_text}"

    def convert(self, lyrics: list[LyricLine], output_path: Path) -> None:
        """
        Convert lyrics to LRC format and write to file.

        Args:
            lyrics: List of lyric lines to convert
            output_path: Path to write LRC file
        """
        if self.compact:
            self._convert_compact(lyrics, output_path)
        else:
            self._convert_standard(lyrics, output_path)

    def _convert_standard(self, lyrics: list[LyricLine], output_path: Path) -> None:
        """Convert to standard LRC format."""
        lines = []

        # Add metadata tags
        lines.extend(self._generate_metadata_tags())

        # Add lyric lines
        for i, lyric in enumerate(lyrics):
            line = self._generate_line(lyric)
            if line is not None:
                lines.append(line)

            # Skip gap/break logic for comment lines
            if lyric.is_comment:
                continue

            # Add break line if effect contains "break"
            if lyric.effect and "break" in lyric.effect.lower():
                lines.append(self._format_timestamp(lyric.end_time))

            # Add gap line if there's a significant gap to the next line
            elif self.line_gap > 0 and i < len(lyrics) - 1:
                next_lyric = lyrics[i + 1]

                # In simple mode, use original_end_time instead of syllable-based end_time
                # This makes the output more readable by using the ASS line timing
                current_end = (
                    lyric.original_end_time
                    if (not self.enhanced and lyric.original_end_time)
                    else lyric.end_time
                )

                # Calculate gap to next line (comment or dialogue)
                gap_duration = next_lyric.start_time - current_end

                # Add gap if the actual gap meets or exceeds the threshold
                if gap_duration >= self.line_gap:
                    lines.append(self._format_timestamp(current_end))

        # Add empty timestamped line at the end based on last dialogue line
        if lyrics:
            # Find the last non-comment line
            last_dialogue = None
            for lyric in reversed(lyrics):
                if not lyric.is_comment:
                    last_dialogue = lyric
                    break

            if last_dialogue:
                # In simple mode, use original_end_time for more readable output
                end_time = (
                    last_dialogue.original_end_time
                    if (not self.enhanced and last_dialogue.original_end_time)
                    else last_dialogue.end_time
                )
                lines.append(self._format_timestamp(end_time))

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    def _convert_compact(self, lyrics: list[LyricLine], output_path: Path) -> None:
        """Convert to compact LRC format (multiple timestamps per line)."""
        lines = []

        # Add metadata tags
        lines.extend(self._generate_metadata_tags())

        # Group lyrics by text content
        text_to_times: dict[str, list[float]] = {}
        for lyric in lyrics:
            # Generate the lyric content (without timestamp)
            if self.enhanced and lyric.syllables:
                enhanced_text = self._format_inline_timestamp(lyric.start_time)
                for i, syllable in enumerate(lyric.syllables):
                    enhanced_text += syllable.text
                    if syllable.text and i < len(lyric.syllables) - 1:
                        enhanced_text += self._format_inline_timestamp(syllable.end_time)
                content = enhanced_text
            else:
                content = lyric.text

            if content not in text_to_times:
                text_to_times[content] = []
            text_to_times[content].append(lyric.start_time)

        # Generate compact format lines
        for content, times in text_to_times.items():
            timestamps = "".join(self._format_timestamp(t) for t in sorted(times))
            lines.append(f"{timestamps}{content}")

        # Add gap lines if configured
        if self.line_gap > 0:
            gap_times = []
            for i, lyric in enumerate(lyrics):
                if i < len(lyrics) - 1:
                    next_lyric = lyrics[i + 1]
                    gap_duration = next_lyric.start_time - lyric.end_time
                    # Only add gap if the actual gap exceeds the threshold
                    if gap_duration > self.line_gap:
                        gap_times.append(lyric.end_time)

            if gap_times:
                gap_line = "".join(self._format_timestamp(t) for t in sorted(gap_times))
                lines.append(gap_line)

        # Add empty timestamped line at the end
        if lyrics:
            lines.append(self._format_timestamp(lyrics[-1].end_time))

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
