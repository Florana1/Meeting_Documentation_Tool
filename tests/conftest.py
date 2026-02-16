"""Shared test fixtures."""

from pathlib import Path

import pytest

from meeting_tool.models import (
    AlignedUtterance,
    DiarizationSegment,
    MeetingSummary,
    MeetingTranscript,
    TranscriptionSegment,
    TranscriptionWord,
)


@pytest.fixture
def sample_diarization_segments():
    """Sample diarization segments for testing."""
    return [
        DiarizationSegment(start=0.0, end=3.0, speaker_label="SPEAKER_00"),
        DiarizationSegment(start=3.5, end=7.0, speaker_label="SPEAKER_01"),
        DiarizationSegment(start=7.5, end=12.0, speaker_label="SPEAKER_00"),
        DiarizationSegment(start=12.5, end=16.0, speaker_label="SPEAKER_02"),
    ]


@pytest.fixture
def sample_transcription_segments():
    """Sample transcription segments with word timestamps."""
    return [
        TranscriptionSegment(
            start=0.0, end=3.0, text="Hello everyone welcome to the meeting",
            words=[
                TranscriptionWord(start=0.0, end=0.5, text="Hello"),
                TranscriptionWord(start=0.5, end=1.0, text="everyone"),
                TranscriptionWord(start=1.0, end=1.5, text="welcome"),
                TranscriptionWord(start=1.5, end=2.0, text="to"),
                TranscriptionWord(start=2.0, end=2.5, text="the"),
                TranscriptionWord(start=2.5, end=3.0, text="meeting"),
            ],
        ),
        TranscriptionSegment(
            start=3.5, end=7.0, text="Thanks Alice lets start with the agenda",
            words=[
                TranscriptionWord(start=3.5, end=4.0, text="Thanks"),
                TranscriptionWord(start=4.0, end=4.5, text="Alice"),
                TranscriptionWord(start=4.5, end=5.0, text="lets"),
                TranscriptionWord(start=5.0, end=5.5, text="start"),
                TranscriptionWord(start=5.5, end=6.0, text="with"),
                TranscriptionWord(start=6.0, end=6.5, text="the"),
                TranscriptionWord(start=6.5, end=7.0, text="agenda"),
            ],
        ),
        TranscriptionSegment(
            start=7.5, end=12.0, text="Sure the first item is the project update",
            words=[
                TranscriptionWord(start=7.5, end=8.0, text="Sure"),
                TranscriptionWord(start=8.0, end=8.5, text="the"),
                TranscriptionWord(start=8.5, end=9.0, text="first"),
                TranscriptionWord(start=9.0, end=9.5, text="item"),
                TranscriptionWord(start=9.5, end=10.0, text="is"),
                TranscriptionWord(start=10.0, end=10.5, text="the"),
                TranscriptionWord(start=10.5, end=11.0, text="project"),
                TranscriptionWord(start=11.0, end=12.0, text="update"),
            ],
        ),
    ]


@pytest.fixture
def sample_utterances():
    """Sample aligned utterances for testing."""
    return [
        AlignedUtterance(
            speaker_label="SPEAKER_00", speaker_name="Alice",
            start=0.0, end=3.0,
            text="Hello everyone welcome to the meeting",
        ),
        AlignedUtterance(
            speaker_label="SPEAKER_01", speaker_name="Bob",
            start=3.5, end=7.0,
            text="Thanks Alice lets start with the agenda",
        ),
        AlignedUtterance(
            speaker_label="SPEAKER_00", speaker_name="Alice",
            start=7.5, end=12.0,
            text="Sure the first item is the project update",
        ),
    ]


@pytest.fixture
def sample_transcript(sample_utterances):
    """Sample meeting transcript for testing."""
    return MeetingTranscript(
        source_file=Path("test_meeting.mp4"),
        duration_seconds=720.0,
        utterances=sample_utterances,
        speaker_map={"SPEAKER_00": "Alice", "SPEAKER_01": "Bob"},
    )


@pytest.fixture
def sample_summary():
    """Sample meeting summary for testing."""
    return MeetingSummary(
        overview="The team discussed project updates and next steps.",
        key_points=[
            "Project is on track for Q1 delivery",
            "New feature requirements were reviewed",
        ],
        action_items=[
            "Alice will send the updated timeline by Friday",
            "Bob will review the design document",
        ],
        decisions=[
            "Team agreed to use the new API framework",
        ],
    )
