"""LRC format expander - converts compact to standard format."""

import re
from pathlib import Path


class LRCExpander:
    """Expands compact LRC format to standard sorted format."""

    @staticmethod
    def _extract_timestamps(line: str) -> tuple[list[float], str]:
        """Extract timestamps and content from a line."""
        # Pattern to match [mm:ss.xx] timestamps
        timestamp_pattern = r"\[(\d{2}):(\d{2}\.\d{2})\]"
        matches = list(re.finditer(timestamp_pattern, line))

        timestamps = []
        for match in matches:
            minutes = int(match.group(1))
            seconds = float(match.group(2))
            total_seconds = minutes * 60 + seconds
            timestamps.append(total_seconds)

        # Extract content after all timestamps
        content = re.sub(timestamp_pattern, "", line, count=len(matches))
        return timestamps, content

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """Format seconds as LRC timestamp [mm:ss.xx]."""
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"[{minutes:02d}:{secs:05.2f}]"

    def expand(self, input_path: Path, output_path: Path) -> None:
        """
        Expand compact LRC to standard format.

        Args:
            input_path: Path to compact LRC file
            output_path: Path to write expanded LRC file
        """
        with open(input_path, encoding="utf-8") as f:
            lines = f.readlines()

        expanded_lines = []
        metadata_lines = []
        timed_entries = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if it's a metadata tag
            if line.startswith("[") and ":" in line and not line[1:3].isdigit():
                metadata_lines.append(line)
                continue

            # Extract timestamps and content
            timestamps, content = self._extract_timestamps(line)

            # If no timestamps found, skip
            if not timestamps:
                continue

            # Create entries for each timestamp
            for timestamp in timestamps:
                timed_entries.append((timestamp, content))

        # Sort by timestamp
        timed_entries.sort(key=lambda x: x[0])

        # Build output
        expanded_lines.extend(metadata_lines)

        for timestamp, content in timed_entries:
            formatted_line = f"{self._format_timestamp(timestamp)}{content}"
            expanded_lines.append(formatted_line)

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(expanded_lines) + "\n")
