
from snuffer.models import DamageType, Warning
from snuffer.modes.filter import _deduplicate


def _make_warning(
    chunk_index: int = 0,
    start: int = 0,
    end: int = 10,
    certainty: str = "SUSPICIOUS",
    damage_types: list[DamageType] | None = None,
) -> Warning:
    return Warning(
        chunk_index=chunk_index,
        chunk_begin=0,
        chunk_end=100,
        start=start,
        end=end,
        threat="test threat",
        damage_types=damage_types or [DamageType.INSTRUCTION_OVERRIDE],
        certainty=certainty,  # type: ignore[arg-type]
    )


def test_dedup_same_position_keeps_higher_certainty():
    w1 = _make_warning(start=0, certainty="CAUTION")
    w2 = _make_warning(start=5, certainty="CLEARLY_MALICIOUS")
    result = _deduplicate([w1, w2])
    assert len(result) == 1
    assert result[0].certainty == "CLEARLY_MALICIOUS"


def test_dedup_different_positions_both_kept():
    w1 = _make_warning(start=0, certainty="SUSPICIOUS")
    w2 = _make_warning(start=200, certainty="SUSPICIOUS")
    result = _deduplicate([w1, w2])
    assert len(result) == 2


def test_dedup_different_damage_types_both_kept():
    w1 = _make_warning(start=0, damage_types=[DamageType.INSTRUCTION_OVERRIDE])
    w2 = _make_warning(start=5, damage_types=[DamageType.REMOTE_CODE_EXECUTION])
    result = _deduplicate([w1, w2])
    assert len(result) == 2
