import anthropic

from snuffer.bracketer import Bracketer
from snuffer.chunker import chunk_text
from snuffer.models import CERTAINTY_RANK, Chunk, SnufferResult, Warning
from snuffer.normalizer import normalize
from snuffer.reviewer import review_chunk
from snuffer.sanitizer import strip_brackets

_DEDUP_WINDOW = 50


def _deduplicate(warnings: list[Warning]) -> list[Warning]:
    result: list[Warning] = []
    for w in warnings:
        duplicate = False
        for existing in result:
            if (
                abs(w.start - existing.start) <= _DEDUP_WINDOW
                and set(w.damage_types) == set(existing.damage_types)
            ):
                if CERTAINTY_RANK[w.certainty] > CERTAINTY_RANK[existing.certainty]:
                    result.remove(existing)
                    result.append(w)
                duplicate = True
                break
        if not duplicate:
            result.append(w)
    return result


async def run_review(
    text: str,
    chunk_size: int = 400,
    overlap_words: int = 40,
) -> SnufferResult:
    normalized = normalize(text)
    sanitized = strip_brackets(normalized)
    chunks: list[Chunk] = chunk_text(sanitized, chunk_size, overlap_words)

    bracketer = Bracketer()
    client = anthropic.AsyncAnthropic()

    all_warnings: list[Warning] = []
    for chunk in chunks:
        bracketed = bracketer.wrap(chunk)
        chunk_warnings = await review_chunk(chunk, bracketed, bracketer.key, client)
        all_warnings.extend(chunk_warnings)

    deduped = _deduplicate(all_warnings)

    return SnufferResult(
        warnings=deduped,
        chunks=chunks,
        normalized_text=sanitized,
        original_text=text,
    )
