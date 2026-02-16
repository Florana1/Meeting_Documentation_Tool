"""Tests for the speaker mapping module."""

from meeting_tool.models import AlignedUtterance
from meeting_tool.speaker_mapping import (
    apply_speaker_names,
    find_speaker_labels,
    parse_speaker_string,
    rename_speakers_in_text,
)


def test_parse_speaker_string_basic():
    result = parse_speaker_string("SPEAKER_00=Alice,SPEAKER_01=Bob")
    assert result == {"SPEAKER_00": "Alice", "SPEAKER_01": "Bob"}


def test_parse_speaker_string_with_spaces():
    result = parse_speaker_string("SPEAKER_00 = Alice , SPEAKER_01 = Bob")
    assert result == {"SPEAKER_00": "Alice", "SPEAKER_01": "Bob"}


def test_parse_speaker_string_single():
    result = parse_speaker_string("SPEAKER_00=Alice")
    assert result == {"SPEAKER_00": "Alice"}


def test_parse_speaker_string_empty():
    result = parse_speaker_string("")
    assert result == {}


def test_parse_speaker_string_invalid_entries():
    result = parse_speaker_string("SPEAKER_00=Alice,invalid,SPEAKER_01=Bob")
    assert result == {"SPEAKER_00": "Alice", "SPEAKER_01": "Bob"}


def test_apply_speaker_names(sample_utterances):
    mapping = {"SPEAKER_00": "Alice", "SPEAKER_01": "Bob"}
    result = apply_speaker_names(sample_utterances, mapping)

    assert result[0].speaker_name == "Alice"
    assert result[1].speaker_name == "Bob"
    assert result[2].speaker_name == "Alice"
    # Labels should remain unchanged
    assert result[0].speaker_label == "SPEAKER_00"
    assert result[1].speaker_label == "SPEAKER_01"


def test_apply_speaker_names_partial_mapping():
    utterances = [
        AlignedUtterance(
            speaker_label="SPEAKER_00", speaker_name="SPEAKER_00",
            start=0.0, end=1.0, text="Hello",
        ),
        AlignedUtterance(
            speaker_label="SPEAKER_01", speaker_name="SPEAKER_01",
            start=1.0, end=2.0, text="Hi",
        ),
    ]
    mapping = {"SPEAKER_00": "Alice"}  # SPEAKER_01 not mapped
    result = apply_speaker_names(utterances, mapping)

    assert result[0].speaker_name == "Alice"
    assert result[1].speaker_name == "SPEAKER_01"  # Falls back to label


def test_apply_speaker_names_empty_mapping(sample_utterances):
    result = apply_speaker_names(sample_utterances, {})

    # Should keep original speaker labels as names
    assert result[0].speaker_name == "SPEAKER_00"
    assert result[1].speaker_name == "SPEAKER_01"


def test_find_speaker_labels():
    text = "**SPEAKER_00** (00:00:05):\nHello\n\n**SPEAKER_01** (00:00:10):\nHi"
    result = find_speaker_labels(text)
    assert result == ["SPEAKER_00", "SPEAKER_01"]


def test_find_speaker_labels_none():
    text = "**Alice** (00:00:05):\nHello"
    result = find_speaker_labels(text)
    assert result == []


def test_find_speaker_labels_duplicates():
    text = "SPEAKER_00 said hello. SPEAKER_00 said goodbye."
    result = find_speaker_labels(text)
    assert result == ["SPEAKER_00"]


def test_rename_speakers_in_text():
    text = (
        "**Participants:** SPEAKER_00, SPEAKER_01\n"
        "SPEAKER_00 raised a concern.\n"
        "**SPEAKER_00** (00:00:05):\nHello\n"
        "**SPEAKER_01** (00:00:10):\nHi\n"
    )
    mapping = {"SPEAKER_00": "Alice", "SPEAKER_01": "Bob"}
    result = rename_speakers_in_text(text, mapping)

    assert "SPEAKER_00" not in result
    assert "SPEAKER_01" not in result
    assert "**Participants:** Alice, Bob" in result
    assert "Alice raised a concern." in result
    assert "**Alice** (00:00:05):" in result
    assert "**Bob** (00:00:10):" in result


def test_rename_speakers_partial_mapping():
    text = "**SPEAKER_00**: Hello\n**SPEAKER_01**: Hi"
    mapping = {"SPEAKER_00": "Alice"}
    result = rename_speakers_in_text(text, mapping)

    assert "**Alice**: Hello" in result
    assert "**SPEAKER_01**: Hi" in result
