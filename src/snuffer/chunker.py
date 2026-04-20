import secrets

from snuffer.models import Chunk


def chunk_text(text: str, chunk_size: int = 400, overlap_words: int = 40) -> list[Chunk]:
    words = text.split()
    if not words:
        return []

    word_positions: list[int] = []
    pos = 0
    for word in words:
        idx = text.index(word, pos)
        word_positions.append(idx)
        pos = idx + len(word)

    chunks: list[Chunk] = []
    chunk_index = 0
    word_idx = 0

    while word_idx < len(words):
        jitter = secrets.randbelow(11)  # 0–10 inclusive, cryptographically unpredictable
        end_word_idx = min(word_idx + chunk_size + jitter, len(words))
        chunk_words = words[word_idx:end_word_idx]
        chunk_text_str = " ".join(chunk_words)

        begin = word_positions[word_idx]
        last_word_idx = end_word_idx - 1
        end = word_positions[last_word_idx] + len(words[last_word_idx])

        chunks.append(Chunk(text=chunk_text_str, begin=begin, end=end, index=chunk_index))
        chunk_index += 1

        if end_word_idx >= len(words):
            break
        word_idx = end_word_idx - overlap_words

    return chunks
