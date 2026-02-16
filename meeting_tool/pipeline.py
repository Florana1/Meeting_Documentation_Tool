"""Orchestrates the full meeting processing pipeline."""

from pathlib import Path

import click

from .audio import prepare_audio, get_audio_duration
from .diarization import run_diarization
from .transcription import run_transcription
from .alignment import align_transcript
from .speaker_mapping import (
    apply_speaker_names,
    interactive_speaker_naming,
    parse_speaker_string,
)
from .summarization import save_prompt_file, summarize_meeting
from .output_formatter import format_meeting_minutes, write_output
from .models import MeetingSummary, MeetingTranscript


def process_meeting(
    input_path: Path,
    output_path: Path | None = None,
    speakers: str | None = None,
    num_speakers: int | None = None,
    whisper_model: str = "large-v3",
    summary: bool = False,
    no_interactive: bool = False,
    device: str = "cpu",
) -> Path:
    """Run the full meeting processing pipeline.

    Args:
        input_path: Path to the input file (.m4a, .mp4, etc.).
        output_path: Path for the output .md file.
        speakers: CLI speaker mapping string (e.g., "SPEAKER_00=Alice,SPEAKER_01=Bob").
        num_speakers: Expected number of speakers (hint for diarization).
        whisper_model: Whisper model size to use.
        summary: Use Claude API for automatic summarization.
        no_interactive: Skip interactive speaker naming.
        device: Device to run models on ("cpu" or "cuda").

    Returns:
        Path to the output .md file.
    """
    if output_path is None:
        output_path = input_path.with_suffix(".md")

    # Step 1: Prepare audio
    click.echo("\n[1/7] Preparing audio...")
    needs_cleanup = input_path.suffix.lower() != ".wav"
    audio_path = prepare_audio(input_path)
    duration = get_audio_duration(audio_path)

    # Step 2: Diarize speakers
    click.echo("\n[2/7] Running speaker diarization...")
    diarization_segments = run_diarization(
        audio_path, num_speakers=num_speakers, device=device
    )

    # Step 3: Transcribe audio
    click.echo("\n[3/7] Transcribing audio...")
    transcription_segments = run_transcription(
        audio_path, model_size=whisper_model, device=device
    )

    # Step 4: Align transcription with diarization
    click.echo("\n[4/7] Aligning transcript with speakers...")
    utterances = align_transcript(transcription_segments, diarization_segments)
    click.echo(f"  Aligned {len(utterances)} utterances")

    # Step 5: Name speakers
    click.echo("\n[5/7] Mapping speaker names...")
    if speakers:
        speaker_map = parse_speaker_string(speakers)
    elif no_interactive:
        speaker_map = {}
    else:
        speaker_map = interactive_speaker_naming(utterances)

    utterances = apply_speaker_names(utterances, speaker_map)

    # Step 6: Summarize
    meeting_summary: MeetingSummary | None = None
    if summary:
        click.echo("\n[6/7] Generating summary via API...")
        meeting_summary = summarize_meeting(utterances)
        click.echo("  Summary generated")
    else:
        click.echo("\n[6/7] Saving prompt file for manual summarization...")
        prompt_path = output_path.with_suffix(".prompt.txt")
        save_prompt_file(utterances, prompt_path)

    # Step 7: Format and write output
    click.echo("\n[7/7] Writing output...")
    transcript = MeetingTranscript(
        source_file=input_path,
        duration_seconds=duration,
        utterances=utterances,
        speaker_map=speaker_map,
    )
    content = format_meeting_minutes(transcript, meeting_summary)
    result_path = write_output(content, output_path)

    click.echo(f"\nDone! Meeting minutes saved to: {result_path}")
    if not summary:
        click.echo(f"  To add a summary, paste {output_path.with_suffix('.prompt.txt').name} into any LLM.")

    # Clean up temporary wav file (only if we created it from a non-wav source)
    if needs_cleanup and audio_path.exists() and audio_path.suffix == ".wav":
        audio_path.unlink()
        click.echo(f"  Cleaned up temporary file: {audio_path.name}")

    return result_path
