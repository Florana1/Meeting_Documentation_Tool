"""Speech-to-text transcription using faster-whisper."""

from pathlib import Path

import click
from faster_whisper import WhisperModel

from .models import TranscriptionSegment, TranscriptionWord


def run_transcription(
    audio_path: Path,
    model_size: str = "large-v3",
    device: str = "cpu",
) -> list[TranscriptionSegment]:
    """Transcribe audio using faster-whisper with word-level timestamps.

    Args:
        audio_path: Path to the .wav audio file.
        model_size: Whisper model size (e.g., "large-v3", "medium", "small").
        device: Device to run on ("cpu" or "cuda").

    Returns:
        List of TranscriptionSegment with word-level timestamps.
    """
    compute_type = "float16" if device == "cuda" else "int8"

    click.echo(f"  Loading Whisper model ({model_size})...")
    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    click.echo("  Transcribing audio...")
    segments_iter, info = model.transcribe(
        str(audio_path),
        language="en",
        word_timestamps=True,
        vad_filter=True,
    )

    segments = []
    for segment in segments_iter:
        words = []
        if segment.words:
            for word in segment.words:
                words.append(TranscriptionWord(
                    start=word.start,
                    end=word.end,
                    text=word.word.strip(),
                ))

        segments.append(TranscriptionSegment(
            start=segment.start,
            end=segment.end,
            text=segment.text.strip(),
            words=words,
        ))

    total_words = sum(len(s.words) for s in segments)
    click.echo(f"  Transcription complete: {len(segments)} segments, {total_words} words")
    return segments
