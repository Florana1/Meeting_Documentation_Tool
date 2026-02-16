"""Convert audio/video files to WAV format for processing."""

import shutil
from pathlib import Path

import click
from pydub import AudioSegment

SUPPORTED_EXTENSIONS = {".m4a", ".mp4", ".wav", ".mp3", ".ogg", ".flac", ".webm"}


def check_ffmpeg() -> bool:
    """Check if ffmpeg is available on PATH."""
    return shutil.which("ffmpeg") is not None


def prepare_audio(input_path: Path, output_path: Path | None = None) -> Path:
    """Convert an audio or video file to 16kHz mono .wav for processing.

    Accepts .m4a (Zoom audio), .mp4 (Zoom video), and other common formats.
    If the input is already a 16kHz mono .wav, it is used directly.

    Args:
        input_path: Path to the input audio/video file.
        output_path: Path for the output .wav file. Defaults to same name with .wav extension.

    Returns:
        Path to the .wav file ready for processing.
    """
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    if input_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file format: {input_path.suffix}\n"
            f"Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    if not check_ffmpeg():
        raise RuntimeError(
            "ffmpeg not found on PATH. Install it:\n"
            "  Windows: winget install ffmpeg\n"
            "  macOS: brew install ffmpeg\n"
            "  Linux: sudo apt install ffmpeg"
        )

    if output_path is None:
        output_path = input_path.with_suffix(".wav")

    click.echo(f"  Converting {input_path.name} to WAV...")
    audio = AudioSegment.from_file(str(input_path))
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(str(output_path), format="wav")
    click.echo(f"  Audio ready: {output_path.name} ({len(audio) / 1000:.1f}s)")

    return output_path


def get_audio_duration(audio_path: Path) -> float:
    """Get duration of an audio file in seconds."""
    audio = AudioSegment.from_file(str(audio_path))
    return len(audio) / 1000.0
