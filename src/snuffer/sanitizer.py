import re

SNUF_PATTERN = re.compile(r"⟪SNUF:[0-9a-f]{8}:[BE]⟫")


def strip_brackets(text: str) -> str:
    prev = None
    while prev != text:
        prev = text
        text = SNUF_PATTERN.sub("", text)
    return text
