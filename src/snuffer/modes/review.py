import asyncio

import anthropic

from snuffer.bracketer import Bracketer
from snuffer.chunker import chunk_text
from snuffer.models import CERTAINTY_RANK, Chunk, SnufferResult, Warning
from snuffer.normalizer import normalize
from snuffer.reviewer import review_chunk
from snuffer.sanitizer import strip_brackets

_DEDUP_WINDOW = 50
_PRIOR_CONTEXT_WORDS = 40


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


def _extract_prior_context(chunk: Chunk, n_words: int = _PRIOR_CONTEXT_WORDS) -> str:
    words = chunk.text.split()
    return " ".join(words[-n_words:])


async def _review_sequential(
    chunks: list[Chunk],
    bracketer: Bracketer,
    client: anthropic.AsyncAnthropic,
    sliding_context: bool,
) -> list[Warning]:
    all_warnings: list[Warning] = []
    prior_context: str | None = None
    for chunk in chunks:
        bracketed = bracketer.wrap(chunk)
        ctx = prior_context if sliding_context else None
        chunk_warnings = await review_chunk(chunk, bracketed, bracketer.key, client, ctx)
        all_warnings.extend(chunk_warnings)
        if sliding_context:
            prior_context = _extract_prior_context(chunk)
    return all_warnings


async def _review_parallel(
    chunks: list[Chunk],
    bracketer: Bracketer,
    client: anthropic.AsyncAnthropic,
    max_concurrent: int,
) -> list[Warning]:
    semaphore = asyncio.Semaphore(max_concurrent)

    async def review_with_limit(chunk: Chunk) -> list[Warning]:
        async with semaphore:
            bracketed = bracketer.wrap(chunk)
            return await review_chunk(chunk, bracketed, bracketer.key, client)

    results = await asyncio.gather(*[review_with_limit(c) for c in chunks])
    all_warnings: list[Warning] = []
    for chunk_warnings in results:
        all_warnings.extend(chunk_warnings)
    return all_warnings


async def run_review(
    text: str,
    chunk_size: int = 400,
    overlap_words: int = 40,
    sliding_context: bool = True,
    parallel: bool = False,
    max_concurrent: int = 5,
) -> SnufferResult:
    normalized = normalize(text)
    sanitized = strip_brackets(normalized)
    chunks: list[Chunk] = chunk_text(sanitized, chunk_size, overlap_words)

    bracketer = Bracketer()
    client = anthropic.AsyncAnthropic()

    if parallel:
        all_warnings = await _review_parallel(chunks, bracketer, client, max_concurrent)
    else:
        all_warnings = await _review_sequential(chunks, bracketer, client, sliding_context)

    deduped = _deduplicate(all_warnings)

    return SnufferResult(
        warnings=deduped,
        chunks=chunks,
        normalized_text=sanitized,
        original_text=text,
    )
