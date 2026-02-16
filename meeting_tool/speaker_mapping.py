"""Interactive and CLI-based speaker name mapping."""

import re

import click

from .models import AlignedUtterance


def parse_speaker_string(speaker_string: str) -> dict[str, str]:
    """Parse a CLI speaker mapping string into a dictionary.

    Format: "SPEAKER_00=Alice,SPEAKER_01=Bob"

    Args:
        speaker_string: Comma-separated speaker label=name pairs.

    Returns:
        Dictionary mapping speaker labels to names.
    """
    mapping = {}
    for pair in speaker_string.split(","):
        pair = pair.strip()
        if "=" not in pair:
            continue
        label, name = pair.split("=", 1)
        mapping[label.strip()] = name.strip()
    return mapping


def _get_sample_utterances(
    utterances: list[AlignedUtterance],
    speaker_label: str,
    max_samples: int = 3,
) -> list[str]:
    """Get sample utterances for a speaker to help with identification."""
    samples = []
    for utt in utterances:
        if utt.speaker_label == speaker_label and len(utt.text) > 10:
            preview = utt.text[:120] + ("..." if len(utt.text) > 120 else "")
            samples.append(preview)
            if len(samples) >= max_samples:
                break
    return samples


def interactive_speaker_naming(
    utterances: list[AlignedUtterance],
) -> dict[str, str]:
    """Interactively prompt the user to name each speaker.

    Shows sample utterances for each speaker label and asks for a name.

    Args:
        utterances: List of aligned utterances with speaker labels.

    Returns:
        Dictionary mapping speaker labels to user-provided names.
    """
    labels = sorted(set(utt.speaker_label for utt in utterances))

    click.echo(f"\n  {len(labels)} speakers detected. Please name them:")
    click.echo("  (Press Enter to keep the default label)\n")

    mapping = {}
    for label in labels:
        samples = _get_sample_utterances(utterances, label)
        click.echo(f"  {label}:")
        for sample in samples:
            click.echo(f'    "{sample}"')

        name = click.prompt(f"  Name for {label}", default=label, show_default=True)
        mapping[label] = name
        click.echo()

    return mapping


def apply_speaker_names(
    utterances: list[AlignedUtterance],
    speaker_map: dict[str, str],
) -> list[AlignedUtterance]:
    """Apply speaker names to utterances based on the mapping.

    Args:
        utterances: List of aligned utterances.
        speaker_map: Dictionary mapping speaker labels to names.

    Returns:
        New list of utterances with speaker_name fields updated.
    """
    return [
        AlignedUtterance(
            speaker_label=utt.speaker_label,
            speaker_name=speaker_map.get(utt.speaker_label, utt.speaker_label),
            start=utt.start,
            end=utt.end,
            text=utt.text,
        )
        for utt in utterances
    ]


def find_speaker_labels(text: str) -> list[str]:
    """Find all unique speaker labels (e.g., SPEAKER_00) in text.

    Args:
        text: Markdown or plain text content.

    Returns:
        Sorted list of unique speaker labels found.
    """
    return sorted(set(re.findall(r"SPEAKER_\d+", text)))


def rename_speakers_in_text(text: str, speaker_map: dict[str, str]) -> str:
    """Replace speaker labels with real names throughout text.

    Args:
        text: Markdown or plain text content.
        speaker_map: Dictionary mapping speaker labels to names.

    Returns:
        Updated text with all speaker labels replaced.
    """
    for label, name in speaker_map.items():
        text = text.replace(label, name)
    return text
