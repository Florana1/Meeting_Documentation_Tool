"""Align transcription words with diarization speaker segments."""

import bisect

from .models import (
    AlignedUtterance,
    DiarizationSegment,
    TranscriptionSegment,
    TranscriptionWord,
)

# Maximum gap between same-speaker utterances before splitting
MERGE_GAP_SECONDS = 1.5


def _compute_overlap(word: TranscriptionWord, segment: DiarizationSegment) -> float:
    """Compute the time overlap between a word and a diarization segment."""
    overlap_start = max(word.start, segment.start)
    overlap_end = min(word.end, segment.end)
    return max(0.0, overlap_end - overlap_start)


def _find_best_speaker(
    word: TranscriptionWord,
    diarization_segments: list[DiarizationSegment],
    segment_starts: list[float],
) -> str:
    """Find the speaker with maximum overlap for a given word.

    Uses binary search to efficiently find candidate segments.
    Falls back to nearest segment if the word falls in a gap.
    """
    if not diarization_segments:
        return "UNKNOWN"

    word_mid = (word.start + word.end) / 2

    # Binary search for the insertion point of the word's midpoint
    idx = bisect.bisect_right(segment_starts, word_mid) - 1
    idx = max(0, idx)

    # Check nearby segments for best overlap
    best_speaker = diarization_segments[idx].speaker_label
    best_overlap = 0.0

    search_range = range(max(0, idx - 1), min(len(diarization_segments), idx + 3))
    for i in search_range:
        overlap = _compute_overlap(word, diarization_segments[i])
        if overlap > best_overlap:
            best_overlap = overlap
            best_speaker = diarization_segments[i].speaker_label

    # If no overlap found, assign to the nearest segment
    if best_overlap == 0.0:
        best_dist = float("inf")
        for i in search_range:
            seg = diarization_segments[i]
            dist = min(abs(word_mid - seg.start), abs(word_mid - seg.end))
            if dist < best_dist:
                best_dist = dist
                best_speaker = seg.speaker_label

    return best_speaker


def align_transcript(
    transcription_segments: list[TranscriptionSegment],
    diarization_segments: list[DiarizationSegment],
) -> list[AlignedUtterance]:
    """Align transcription words with diarization segments to produce speaker-labeled utterances.

    Algorithm:
    1. For each transcribed word, find the diarization segment with maximum time overlap.
    2. Group consecutive same-speaker words into utterances.
    3. Merge adjacent same-speaker utterances within MERGE_GAP_SECONDS.

    Args:
        transcription_segments: Transcription output with word timestamps.
        diarization_segments: Diarization output with speaker segments.

    Returns:
        List of AlignedUtterance sorted by start time.
    """
    if not transcription_segments:
        return []

    # Precompute sorted segment start times for binary search
    sorted_diar = sorted(diarization_segments, key=lambda s: s.start)
    segment_starts = [s.start for s in sorted_diar]

    # Collect all words and assign speakers
    speaker_words: list[tuple[str, TranscriptionWord]] = []
    for seg in transcription_segments:
        for word in seg.words:
            speaker = _find_best_speaker(word, sorted_diar, segment_starts)
            speaker_words.append((speaker, word))

    if not speaker_words:
        return []

    # Group consecutive same-speaker words into utterances
    raw_utterances: list[AlignedUtterance] = []
    current_speaker, current_word = speaker_words[0]
    current_words_text = [current_word.text]
    current_start = current_word.start
    current_end = current_word.end

    for speaker, word in speaker_words[1:]:
        if speaker == current_speaker:
            current_words_text.append(word.text)
            current_end = word.end
        else:
            raw_utterances.append(AlignedUtterance(
                speaker_label=current_speaker,
                speaker_name=current_speaker,
                start=current_start,
                end=current_end,
                text=" ".join(current_words_text),
            ))
            current_speaker = speaker
            current_words_text = [word.text]
            current_start = word.start
            current_end = word.end

    # Don't forget the last utterance
    raw_utterances.append(AlignedUtterance(
        speaker_label=current_speaker,
        speaker_name=current_speaker,
        start=current_start,
        end=current_end,
        text=" ".join(current_words_text),
    ))

    # Merge adjacent same-speaker utterances within gap threshold
    merged: list[AlignedUtterance] = [raw_utterances[0]]
    for utt in raw_utterances[1:]:
        prev = merged[-1]
        if (utt.speaker_label == prev.speaker_label
                and utt.start - prev.end < MERGE_GAP_SECONDS):
            merged[-1] = AlignedUtterance(
                speaker_label=prev.speaker_label,
                speaker_name=prev.speaker_name,
                start=prev.start,
                end=utt.end,
                text=prev.text + " " + utt.text,
            )
        else:
            merged.append(utt)

    return merged
