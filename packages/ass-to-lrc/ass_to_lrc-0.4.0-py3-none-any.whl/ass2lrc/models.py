"""Data models for ASS and LRC conversion."""

from dataclasses import dataclass


@dataclass
class Syllable:
    """Represents a syllable with timing information."""

    text: str
    start_time: float
    duration: float

    @property
    def end_time(self) -> float:
        """Calculate end time of syllable."""
        return self.start_time + self.duration


@dataclass
class LyricLine:
    """Represents a single lyric line with timing and syllables."""

    start_time: float
    text: str
    syllables: list[Syllable]
    style: str = "Default"
    name: str = ""
    effect: str = ""
    original_end_time: float | None = None
    is_comment: bool = False

    @property
    def end_time(self) -> float:
        """Calculate end time based on last syllable or original end time."""
        if self.syllables and self.syllables[-1].duration > 0:
            return self.syllables[-1].end_time
        if self.original_end_time is not None:
            return self.original_end_time
        return self.start_time


@dataclass
class Metadata:
    """Represents LRC metadata tags."""

    title: str | None = None
    artist: str | None = None
    album: str | None = None
    author: str | None = None
    lyricist: str | None = None
    length: str | None = None
    by: str | None = None
    offset: str | None = None
    re: str | None = None
    tool: str | None = None
    version: str | None = None
    comments: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize mutable default values."""
        if self.comments is None:
            self.comments = []
