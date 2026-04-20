from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


class DamageType(str, Enum):
    REMOTE_CODE_EXECUTION = "REMOTE_CODE_EXECUTION"
    DATA_EXFILTRATION = "DATA_EXFILTRATION"
    ROLE_MANIPULATION = "ROLE_MANIPULATION"
    INSTRUCTION_OVERRIDE = "INSTRUCTION_OVERRIDE"
    ENCODED_PAYLOAD = "ENCODED_PAYLOAD"
    SOCIAL_ENGINEERING = "SOCIAL_ENGINEERING"
    INDIRECT_INJECTION = "INDIRECT_INJECTION"
    MULTI_STEP_ATTACK = "MULTI_STEP_ATTACK"
    PRIVILEGE_ESCALATION = "PRIVILEGE_ESCALATION"
    DELIMITER_FORGERY = "DELIMITER_FORGERY"
    HOMOGLYPH_ATTACK = "HOMOGLYPH_ATTACK"
    PROMPT_LEAKING = "PROMPT_LEAKING"


Certainty = Literal["CLEARLY_MALICIOUS", "SUSPICIOUS", "CAUTION"]

CERTAINTY_RANK: dict[Certainty, int] = {
    "CAUTION": 0,
    "SUSPICIOUS": 1,
    "CLEARLY_MALICIOUS": 2,
}


@dataclass
class Warning:
    chunk_index: int
    chunk_begin: int
    chunk_end: int
    start: int
    end: int
    threat: str
    damage_types: list[DamageType]
    certainty: Certainty


@dataclass
class Chunk:
    text: str
    begin: int
    end: int
    index: int


@dataclass
class SnufferResult:
    warnings: list[Warning] = field(default_factory=list)
    chunks: list[Chunk] = field(default_factory=list)
    normalized_text: str = ""
    original_text: str = ""
    session_id: str = ""
