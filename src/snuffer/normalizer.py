import base64
import binascii
import re
import unicodedata

from unidecode import unidecode

ZERO_WIDTH_CHARS = re.compile(
    r"[\u200b\u200c\u200d\ufeff\u00ad\u034f\u115f\u1160\u17b4\u17b5"
    r"\u180b-\u180d\u200b-\u200f\u202a-\u202e\u2060-\u206f\ufe00-\ufe0f\uffa0]"
)
RTL_OVERRIDE = re.compile(r"[\u202e\u202d]")
HEX_ESCAPE = re.compile(r"(?:\\x[0-9a-fA-F]{2})+")
BASE64_CANDIDATE = re.compile(r"[A-Za-z0-9+/]{20,}={0,2}")
URL_ENCODED = re.compile(r"(?:%[0-9a-fA-F]{2})+")


def _decode_hex_escapes(text: str) -> str:
    def replace(m: re.Match[str]) -> str:
        try:
            return bytes.fromhex(m.group().replace("\\x", "")).decode("utf-8", errors="replace")
        except Exception:
            return m.group()

    return HEX_ESCAPE.sub(replace, text)


def _decode_url_encoding(text: str) -> str:
    from urllib.parse import unquote

    def replace(m: re.Match[str]) -> str:
        try:
            return unquote(m.group())
        except Exception:
            return m.group()

    return URL_ENCODED.sub(replace, text)


def _decode_base64_candidates(text: str) -> str:
    def replace(m: re.Match[str]) -> str:
        candidate = m.group()
        try:
            decoded = base64.b64decode(candidate + "==").decode("utf-8")
            if decoded.isprintable() and len(decoded) > 5:
                return f"[BASE64:{decoded}]"
        except (binascii.Error, UnicodeDecodeError):
            pass
        return candidate

    return BASE64_CANDIDATE.sub(replace, text)


def _normalize_homoglyphs(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    return unidecode(normalized)


def _strip_zero_width(text: str) -> str:
    text = ZERO_WIDTH_CHARS.sub("", text)
    text = RTL_OVERRIDE.sub("", text)
    return text


def normalize(text: str) -> str:
    text = _strip_zero_width(text)
    text = _decode_hex_escapes(text)
    text = _decode_url_encoding(text)
    text = _decode_base64_candidates(text)
    text = _normalize_homoglyphs(text)
    return text
