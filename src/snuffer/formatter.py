from snuffer.models import CERTAINTY_RANK, Certainty, SnufferResult, Warning


def _highest_certainty(warnings: list[Warning]) -> Certainty | None:
    if not warnings:
        return None
    return max(warnings, key=lambda w: CERTAINTY_RANK[w.certainty]).certainty


def _recommended_action(highest: Certainty | None) -> str:
    if highest is None:
        return "No action required. Input appears clean."
    if highest == "CLEARLY_MALICIOUS":
        return "REJECT input. Clearly malicious content detected."
    if highest == "SUSPICIOUS":
        return "REVIEW manually. Suspicious content found — do not pass to target LLM without inspection."
    return "CAUTION. Low-confidence signals detected — consider manual review."


def format_report(result: SnufferResult) -> str:
    warnings = result.warnings
    chunks = result.chunks

    counts: dict[Certainty, int] = {"CLEARLY_MALICIOUS": 0, "SUSPICIOUS": 0, "CAUTION": 0}
    chunk_summary: dict[int, dict[str, int]] = {}

    for w in warnings:
        counts[w.certainty] += 1
        if w.chunk_index not in chunk_summary:
            chunk_summary[w.chunk_index] = {"CLEARLY_MALICIOUS": 0, "SUSPICIOUS": 0, "CAUTION": 0}
        chunk_summary[w.chunk_index][w.certainty] += 1

    highest = _highest_certainty(warnings)
    action = _recommended_action(highest)

    lines: list[str] = ["# Snuffer Report\n"]

    lines.append("## Summary Table\n")
    lines.append("| Chunk | Chars | CLEARLY_MALICIOUS | SUSPICIOUS | CAUTION |")
    lines.append("|-------|-------|-------------------|------------|---------|")
    for chunk in chunks:
        cs = chunk_summary.get(chunk.index, {})
        lines.append(
            f"| {chunk.index} | {chunk.begin}–{chunk.end} "
            f"| {cs.get('CLEARLY_MALICIOUS', 0)} "
            f"| {cs.get('SUSPICIOUS', 0)} "
            f"| {cs.get('CAUTION', 0)} |"
        )

    lines.append("\n## Severity Breakdown\n")
    lines.append(f"- CLEARLY_MALICIOUS: {counts['CLEARLY_MALICIOUS']}")
    lines.append(f"- SUSPICIOUS: {counts['SUSPICIOUS']}")
    lines.append(f"- CAUTION: {counts['CAUTION']}")

    lines.append("\n## Warnings\n")
    if not warnings:
        lines.append("No warnings detected.")
    else:
        for i, w in enumerate(warnings, 1):
            lines.append(f"### Warning {i} — {w.certainty}")
            lines.append(f"- **Chunk:** {w.chunk_index} (chars {w.chunk_begin}–{w.chunk_end})")
            lines.append(f"- **Position:** chars {w.start}–{w.end}")
            lines.append(f"- **Threat:** {w.threat}")
            lines.append(f"- **Damage types:** {', '.join(dt.value for dt in w.damage_types)}")
            lines.append("")

    lines.append("\n## Recommended Action\n")
    lines.append(action)

    return "\n".join(lines)
