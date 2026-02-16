"""Tests for the output formatter module."""

from meeting_tool.output_formatter import (
    _format_duration,
    _format_timestamp,
    format_meeting_minutes,
)


def test_format_duration_minutes():
    assert _format_duration(300) == "5m"


def test_format_duration_hours():
    assert _format_duration(4980) == "1h 23m"


def test_format_duration_zero():
    assert _format_duration(0) == "0m"


def test_format_timestamp():
    assert _format_timestamp(0) == "00:00:00"
    assert _format_timestamp(65) == "00:01:05"
    assert _format_timestamp(3661) == "01:01:01"


def test_format_meeting_minutes_with_summary(sample_transcript, sample_summary):
    result = format_meeting_minutes(sample_transcript, sample_summary)

    assert "# Meeting Minutes" in result
    assert "Alice" in result
    assert "Bob" in result
    assert "12m" in result  # 720 seconds = 12m
    assert "## Summary" in result
    assert "### Meeting Overview" in result
    assert "project updates" in result
    assert "### Key Points" in result
    assert "### Action Items" in result
    assert "- [ ]" in result
    assert "### Decisions Made" in result
    assert "## Full Transcript" in result
    assert "Hello everyone" in result


def test_format_meeting_minutes_without_summary(sample_transcript):
    result = format_meeting_minutes(sample_transcript, summary=None)

    assert "# Meeting Minutes" in result
    assert "## Summary" not in result
    assert "## Full Transcript" in result
    assert "Hello everyone" in result


def test_transcript_timestamps(sample_transcript):
    result = format_meeting_minutes(sample_transcript)

    assert "(00:00:00)" in result  # first utterance at 0.0s
    assert "(00:00:03)" in result  # second utterance at 3.5s -> 00:00:03
    assert "(00:00:07)" in result  # third utterance at 7.5s -> 00:00:07
