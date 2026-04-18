from typing import Any

import anthropic

from snuffer.bracketer import Bracketer
from snuffer.chunker import chunk_text
from snuffer.models import CERTAINTY_RANK, Certainty, Chunk, Warning
from snuffer.normalizer import normalize
from snuffer.reviewer import review_chunk
from snuffer.sanitizer import strip_brackets

_DEDUP_WINDOW = 50


def _certainty_rank(c: Certainty) -> int:
    return CERTAINTY_RANK[c]


def _deduplicate(warnings: list[Warning]) -> list[Warning]:
    result: list[Warning] = []
    for w in warnings:
        duplicate = False
        for existing in result:
            if (
                abs(w.start - existing.start) <= _DEDUP_WINDOW
                and set(w.damage_types) == set(existing.damage_types)
            ):
                if _certainty_rank(w.certainty) > _certainty_rank(existing.certainty):
                    result.remove(existing)
                    result.append(w)
                duplicate = True
                break
        if not duplicate:
            result.append(w)
    return result


async def run_filter(
    text: str,
    certainty_threshold: Certainty = "SUSPICIOUS",
    min_output_chars: int = 100,
    chunk_size: int = 400,
    overlap_words: int = 40,
) -> dict[str, Any]:
    threshold_rank = _certainty_rank(certainty_threshold)

    normalized = normalize(text)
    sanitized = strip_brackets(normalized)
    chunks: list[Chunk] = chunk_text(sanitized, chunk_size, overlap_words)

    bracketer = Bracketer()
    client = anthropic.AsyncAnthropic()

    all_warnings: list[Warning] = []
    chunk_warnings_map: dict[int, list[Warning]] = {}

    for chunk in chunks:
        bracketed = bracketer.wrap(chunk)
        warnings = await review_chunk(chunk, bracketed, bracketer.key, client)
        chunk_warnings_map[chunk.index] = warnings
        all_warnings.extend(warnings)

    deduped = _deduplicate(all_warnings)

    flagged_chunks: set[int] = set()
    for w in deduped:
        if _certainty_rank(w.certainty) >= threshold_rank:
            flagged_chunks.add(w.chunk_index)

    seen_begins: set[int] = set()
    clean_parts: list[str] = []
    for chunk in chunks:
        if chunk.index not in flagged_chunks and chunk.begin not in seen_begins:
            clean_parts.append(chunk.text)
            seen_begins.add(chunk.begin)

    cleaned_text = " ".join(clean_parts)

    if len(cleaned_text) < min_output_chars:
        return {
            "error": "COMPLETELY_ROTTEN_INPUT",
            "cleaned_text": "",
            "report": {
                "removed_chunks": len(flagged_chunks),
                "total_chunks": len(chunks),
                "warnings": len(deduped),
            },
        }

    return {
        "cleaned_text": cleaned_text,
        "error": None,
        "report": {
            "removed_chunks": len(flagged_chunks),
            "total_chunks": len(chunks),
            "warnings": len(deduped),
            "severity": {
                "CLEARLY_MALICIOUS": sum(1 for w in deduped if w.certainty == "CLEARLY_MALICIOUS"),
                "SUSPICIOUS": sum(1 for w in deduped if w.certainty == "SUSPICIOUS"),
                "CAUTION": sum(1 for w in deduped if w.certainty == "CAUTION"),
            },
        },
    }
