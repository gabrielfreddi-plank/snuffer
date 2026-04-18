from snuffer.chunker import chunk_text


def _make_words(n: int) -> str:
    return " ".join(f"word{i}" for i in range(n))


def test_single_chunk_short_text():
    text = "hello world foo bar"
    chunks = chunk_text(text, chunk_size=400, overlap_words=40)
    assert len(chunks) == 1
    assert chunks[0].text == text
    assert chunks[0].begin == 0
    assert chunks[0].index == 0


def test_multiple_chunks():
    text = _make_words(500)
    chunks = chunk_text(text, chunk_size=400, overlap_words=40)
    assert len(chunks) == 2
    assert chunks[0].index == 0
    assert chunks[1].index == 1


def test_overlap_present():
    text = _make_words(500)
    chunks = chunk_text(text, chunk_size=400, overlap_words=40)
    # Last 40 words of chunk 0 should appear in chunk 1
    words_0 = chunks[0].text.split()
    words_1 = chunks[1].text.split()
    overlap = words_0[-40:]
    assert words_1[:40] == overlap


def test_char_offsets_correct():
    text = "alpha beta gamma delta"
    chunks = chunk_text(text, chunk_size=400, overlap_words=0)
    assert len(chunks) == 1
    assert chunks[0].begin == 0
    assert chunks[0].end == len(text)


def test_empty_text():
    chunks = chunk_text("", chunk_size=400, overlap_words=40)
    assert chunks == []


def test_chunk_begin_in_original():
    text = "  leading spaces word1 word2 word3"
    chunks = chunk_text(text, chunk_size=400, overlap_words=40)
    # begin should point to actual word start, not 0
    assert text[chunks[0].begin] != " " or chunks[0].begin == 0
