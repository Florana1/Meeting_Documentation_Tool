"""Speaker diarization using pyannote.audio."""

import os
from pathlib import Path

import click
import torch
import torchaudio
from pyannote.audio import Pipeline

from .config import get_huggingface_token
from .models import DiarizationSegment


def _load_audio(audio_path: Path) -> dict:
    """Load audio with torchaudio and return a waveform dict.

    This bypasses pyannote's built-in audio decoding (torchcodec),
    which is broken on Windows.
    """
    waveform, sample_rate = torchaudio.load(str(audio_path))
    return {"waveform": waveform, "sample_rate": sample_rate}


def run_diarization(
    audio_path: Path,
    num_speakers: int | None = None,
    device: str = "cpu",
) -> list[DiarizationSegment]:
    """Run speaker diarization on an audio file.

    Args:
        audio_path: Path to the .wav audio file.
        num_speakers: Expected number of speakers (optional hint).
        device: Device to run on ("cpu" or "cuda").

    Returns:
        List of DiarizationSegment sorted by start time.
    """
    token = get_huggingface_token()
    os.environ["HF_TOKEN"] = token

    click.echo("  Loading diarization model...")
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
    )
    pipeline.to(torch.device(device))

    click.echo("  Running speaker diarization...")
    audio = _load_audio(audio_path)

    kwargs = {}
    if num_speakers is not None:
        kwargs["num_speakers"] = num_speakers

    diarization = pipeline(audio, **kwargs)

    segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append(DiarizationSegment(
            start=turn.start,
            end=turn.end,
            speaker_label=speaker,
        ))

    segments.sort(key=lambda s: s.start)
    click.echo(f"  Diarization complete: {len(segments)} segments, "
               f"{len(set(s.speaker_label for s in segments))} speakers detected")
    return segments
