"""Tests for the alignment module."""

from meeting_tool.alignment import align_transcript, _compute_overlap, MERGE_GAP_SECONDS
from meeting_tool.models import (
    DiarizationSegment,
    TranscriptionSegment,
    TranscriptionWord,
)


def test_compute_overlap_full():
    word = TranscriptionWord(start=1.0, end=2.0, text="hello")
    segment = DiarizationSegment(start=0.0, end=3.0, speaker_label="A")
    assert _compute_overlap(word, segment) == 1.0


def test_compute_overlap_partial():
    word = TranscriptionWord(start=1.0, end=3.0, text="hello")
    segment = DiarizationSegment(start=2.0, end=4.0, speaker_label="A")
    assert _compute_overlap(word, segment) == 1.0


def test_compute_overlap_none():
    word = TranscriptionWord(start=1.0, end=2.0, text="hello")
    segment = DiarizationSegment(start=3.0, end=4.0, speaker_label="A")
    assert _compute_overlap(word, segment) == 0.0


def test_align_basic(sample_transcription_segments, sample_diarization_segments):
    result = align_transcript(sample_transcription_segments, sample_diarization_segments)

    assert len(result) > 0
    # First words should be assigned to SPEAKER_00 (diarization segment 0.0-3.0)
    assert result[0].speaker_label == "SPEAKER_00"
    # Second group should be SPEAKER_01 (diarization segment 3.5-7.0)
    assert result[1].speaker_label == "SPEAKER_01"


def test_align_empty_transcription(sample_diarization_segments):
    result = align_transcript([], sample_diarization_segments)
    assert result == []


def test_align_empty_diarization(sample_transcription_segments):
    result = align_transcript(sample_transcription_segments, [])
    # With no diarization segments, all words are assigned to "UNKNOWN"
    assert len(result) == 1
    assert result[0].speaker_label == "UNKNOWN"
    assert "Hello" in result[0].text


def test_align_preserves_text(sample_transcription_segments, sample_diarization_segments):
    result = align_transcript(sample_transcription_segments, sample_diarization_segments)

    all_text = " ".join(utt.text for utt in result)
    # All original words should appear in the output
    assert "Hello" in all_text
    assert "agenda" in all_text
    assert "update" in all_text


def test_merge_adjacent_same_speaker():
    """Adjacent utterances from the same speaker within gap should merge."""
    diar = [
        DiarizationSegment(start=0.0, end=5.0, speaker_label="SPEAKER_00"),
    ]
    trans = [
        TranscriptionSegment(
            start=0.0, end=2.0, text="Hello there",
            words=[
                TranscriptionWord(start=0.0, end=1.0, text="Hello"),
                TranscriptionWord(start=1.0, end=2.0, text="there"),
            ],
        ),
        TranscriptionSegment(
            start=2.5, end=4.5, text="how are you",
            words=[
                TranscriptionWord(start=2.5, end=3.5, text="how"),
                TranscriptionWord(start=3.5, end=4.0, text="are"),
                TranscriptionWord(start=4.0, end=4.5, text="you"),
            ],
        ),
    ]
    result = align_transcript(trans, diar)

    # Should merge into one utterance since same speaker and gap < 1.5s
    assert len(result) == 1
    assert result[0].speaker_label == "SPEAKER_00"
    assert "Hello" in result[0].text
    assert "you" in result[0].text


def test_no_merge_across_speakers():
    """Utterances from different speakers should not merge."""
    diar = [
        DiarizationSegment(start=0.0, end=2.0, speaker_label="SPEAKER_00"),
        DiarizationSegment(start=2.5, end=5.0, speaker_label="SPEAKER_01"),
    ]
    trans = [
        TranscriptionSegment(
            start=0.0, end=2.0, text="Hello",
            words=[TranscriptionWord(start=0.0, end=2.0, text="Hello")],
        ),
        TranscriptionSegment(
            start=2.5, end=5.0, text="Hi",
            words=[TranscriptionWord(start=2.5, end=5.0, text="Hi")],
        ),
    ]
    result = align_transcript(trans, diar)

    assert len(result) == 2
    assert result[0].speaker_label == "SPEAKER_00"
    assert result[1].speaker_label == "SPEAKER_01"
