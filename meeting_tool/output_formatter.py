"""Markdown output generation for meeting minutes."""

from datetime import date
from pathlib import Path

import click

from .models import MeetingSummary, MeetingTranscript


def _format_duration(seconds: float) -> str:
    """Format duration in seconds to a human-readable string."""
    total_minutes = int(seconds) // 60
    hours = total_minutes // 60
    minutes = total_minutes % 60
    if hours > 0:
        return f"{hours}h {minutes:02d}m"
    return f"{minutes}m"


def _format_timestamp(seconds: float) -> str:
    """Format seconds to HH:MM:SS timestamp."""
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_meeting_minutes(
    transcript: MeetingTranscript,
    summary: MeetingSummary | None = None,
) -> str:
    """Format meeting transcript and summary into markdown.

    Args:
        transcript: The complete meeting transcript.
        summary: Optional AI-generated summary.

    Returns:
        Formatted markdown string.
    """
    participants = sorted(set(
        utt.speaker_name for utt in transcript.utterances
    ))
    duration = _format_duration(transcript.duration_seconds)

    lines = [
        "# Meeting Minutes",
        f"**Date:** {date.today().isoformat()}  |  "
        f"**Duration:** {duration}  |  "
        f"**Participants:** {', '.join(participants)}",
        "",
    ]

    if summary:
        lines.append("---")
        lines.append("## Summary")
        lines.append("")
        lines.append("### Meeting Overview")
        lines.append(summary.overview)
        lines.append("")

        if summary.key_points:
            lines.append("### Key Points")
            for point in summary.key_points:
                lines.append(f"- {point}")
            lines.append("")

        if summary.action_items:
            lines.append("### Action Items")
            for item in summary.action_items:
                lines.append(f"- [ ] {item}")
            lines.append("")

        if summary.decisions:
            lines.append("### Decisions Made")
            for decision in summary.decisions:
                lines.append(f"- {decision}")
            lines.append("")

    lines.append("---")
    lines.append("## Full Transcript")
    lines.append("")

    for utt in transcript.utterances:
        timestamp = _format_timestamp(utt.start)
        lines.append(f"**{utt.speaker_name}** ({timestamp}):")
        lines.append(utt.text)
        lines.append("")

    return "\n".join(lines)


def write_output(
    content: str,
    output_path: Path,
) -> Path:
    """Write formatted meeting minutes to a file.

    Args:
        content: The formatted markdown content.
        output_path: Path to write the output file.

    Returns:
        Path to the written file.
    """
    output_path.write_text(content, encoding="utf-8")
    click.echo(f"  Meeting minutes saved to: {output_path}")
    return output_path
