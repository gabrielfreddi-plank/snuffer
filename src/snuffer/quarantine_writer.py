from datetime import datetime, timezone
from pathlib import Path

from snuffer.models import Certainty, SnufferResult

_CERTAINTY_ORDER: list[Certainty] = ["CLEARLY_MALICIOUS", "SUSPICIOUS", "CAUTION"]


def write_quarantine(
    result: SnufferResult,
    original_text: str,
    session_id: str,
    input_filename: str,
    quarantine_dir: str = "quarantine",
) -> Path:
    """Write quarantine file. Returns path of written file."""
    dir_path = Path(quarantine_dir)
    dir_path.mkdir(parents=True, exist_ok=True)

    file_path = dir_path / f"{input_filename}_{session_id}.md"
    timestamp = datetime.now(timezone.utc).isoformat()

    lines: list[str] = [
        "# Quarantine Report",
        f"Session: {session_id}",
        f"Input: {input_filename}",
        f"Timestamp: {timestamp}",
        "",
    ]

    if not result.warnings:
        lines.append("No threats detected.")
    else:
        for certainty in _CERTAINTY_ORDER:
            group = [w for w in result.warnings if w.certainty == certainty]
            if not group:
                continue
            lines.append(f"## {certainty}")
            lines.append("")
            for i, warning in enumerate(group, 1):
                damage_str = ", ".join(d.value for d in warning.damage_types)
                sentence = original_text[warning.start : warning.end]
                lines.append(f"### Warning {i}")
                lines.append(f"- Damage Types: {damage_str}")
                lines.append(f"- Position: chars {warning.start}–{warning.end}")
                lines.append(f"- Sentence: {sentence}")
                lines.append(f"- Description: {warning.threat}")
                lines.append("")

    file_path.write_text("\n".join(lines), encoding="utf-8")
    return file_path
