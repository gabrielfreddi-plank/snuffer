import secrets

from snuffer.models import Chunk


class Bracketer:
    def __init__(self) -> None:
        self.session_key = secrets.token_hex(4)

    def wrap(self, chunk: Chunk) -> str:
        start = f"⟪SNUF:{self.session_key}:B⟫"
        end = f"⟪SNUF:{self.session_key}:E⟫"
        return f"{start} {chunk.text} {end}"

    @property
    def key(self) -> str:
        return self.session_key
