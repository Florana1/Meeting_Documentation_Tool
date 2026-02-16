"""Meeting summarization - prompt generation and optional API summarization."""

import json
from pathlib import Path

import click

from .models import AlignedUtterance, MeetingSummary

SUMMARY_PROMPT = """\
You are a meeting minutes assistant. Given a meeting transcript, produce a structured summary with these sections:

1. **Meeting Overview**: A 2-3 sentence overview of the meeting.
2. **Key Points**: A list of the most important points discussed.
3. **Action Items**: A list of action items with responsible persons and deadlines if mentioned.
4. **Decisions Made**: A list of decisions that were made during the meeting.

Keep each item concise. Format your response in Markdown."""

SUMMARY_PROMPT_JSON = """\
You are a meeting minutes assistant. Given a meeting transcript, produce a structured summary.
Respond with a JSON object containing exactly these keys:
- "overview": A 2-3 sentence overview of the meeting.
- "key_points": A list of the most important points discussed.
- "action_items": A list of action items with responsible persons and deadlines if mentioned.
- "decisions": A list of decisions that were made during the meeting.

Keep each item concise. If a category has no items, use an empty list.
Respond ONLY with the JSON object, no other text."""


def _format_transcript_for_prompt(utterances: list[AlignedUtterance]) -> str:
    """Format utterances into a readable transcript string for the prompt."""
    lines = []
    for utt in utterances:
        minutes = int(utt.start) // 60
        seconds = int(utt.start) % 60
        timestamp = f"{minutes:02d}:{seconds:02d}"
        lines.append(f"[{timestamp}] {utt.speaker_name}: {utt.text}")
    return "\n".join(lines)


def save_prompt_file(utterances: list[AlignedUtterance], output_path: Path) -> Path:
    """Save a ready-to-paste prompt file with the transcript for manual LLM summarization.

    Args:
        utterances: List of speaker-labeled utterances.
        output_path: Path for the prompt .txt file.

    Returns:
        Path to the saved prompt file.
    """
    transcript_text = _format_transcript_for_prompt(utterances)

    content = f"""{SUMMARY_PROMPT}

---

Please summarize this meeting transcript:

{transcript_text}"""

    output_path.write_text(content, encoding="utf-8")
    click.echo(f"  Prompt file saved to: {output_path}")
    click.echo("  -> Paste its contents into any LLM (ChatGPT, Claude, Gemini, etc.) to get your summary.")
    return output_path


def summarize_meeting(utterances: list[AlignedUtterance]) -> MeetingSummary:
    """Send the transcript to Claude API and parse the structured summary.

    Requires the 'anthropic' package and ANTHROPIC_API_KEY in .env.

    Args:
        utterances: List of speaker-labeled utterances.

    Returns:
        MeetingSummary with overview, key points, action items, and decisions.
    """
    try:
        import anthropic
    except ImportError:
        raise RuntimeError(
            "The 'anthropic' package is required for --summary.\n"
            "Install it with: pip install anthropic"
        )

    from .config import get_anthropic_api_key
    api_key = get_anthropic_api_key()
    client = anthropic.Anthropic(api_key=api_key)

    transcript_text = _format_transcript_for_prompt(utterances)

    click.echo("  Generating meeting summary with Claude...")
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        system=SUMMARY_PROMPT_JSON,
        messages=[
            {
                "role": "user",
                "content": f"Please summarize this meeting transcript:\n\n{transcript_text}",
            }
        ],
    )

    response_text = message.content[0].text
    data = json.loads(response_text)

    return MeetingSummary(
        overview=data.get("overview", ""),
        key_points=data.get("key_points", []),
        action_items=data.get("action_items", []),
        decisions=data.get("decisions", []),
    )
