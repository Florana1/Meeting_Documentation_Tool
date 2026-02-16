"""Shared data structures for the meeting documentation pipeline."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DiarizationSegment:
    """A segment where a specific speaker is talking."""
    start: float
    end: float
    speaker_label: str


@dataclass
class TranscriptionWord:
    """A single transcribed word with timing information."""
    start: float
    end: float
    text: str


@dataclass
class TranscriptionSegment:
    """A transcribed segment (sentence/phrase) with word-level timestamps."""
    start: float
    end: float
    text: str
    words: list[TranscriptionWord]


@dataclass
class AlignedUtterance:
    """A speaker-labeled utterance combining diarization and transcription."""
    speaker_label: str
    speaker_name: str
    start: float
    end: float
    text: str


@dataclass
class MeetingTranscript:
    """Complete meeting transcript with speaker-labeled utterances."""
    source_file: Path
    duration_seconds: float
    utterances: list[AlignedUtterance]
    speaker_map: dict[str, str] = field(default_factory=dict)


@dataclass
class MeetingSummary:
    """AI-generated meeting summary."""
    overview: str
    key_points: list[str]
    action_items: list[str]
    decisions: list[str]
