from snuffer.formatter import format_report
from snuffer.models import Chunk, DamageType, SnufferResult, Warning


def _make_result(warnings: list[Warning]) -> SnufferResult:
    chunk = Chunk(text="test text", begin=0, end=9, index=0)
    return SnufferResult(
        warnings=warnings,
        chunks=[chunk],
        normalized_text="test text",
        original_text="test text",
    )


def test_no_warnings_message():
    result = _make_result([])
    report = format_report(result)
    assert "No warnings detected" in report


def test_contains_summary_table():
    result = _make_result([])
    report = format_report(result)
    assert "Summary Table" in report
    assert "Chunk" in report


def test_warning_position_not_text():
    w = Warning(
        chunk_index=0,
        chunk_begin=0,
        chunk_end=100,
        start=5,
        end=50,
        threat="Instruction override detected",
        damage_types=[DamageType.INSTRUCTION_OVERRIDE],
        certainty="CLEARLY_MALICIOUS",
    )
    result = _make_result([w])
    report = format_report(result)
    # positions present
    assert "5" in report
    assert "50" in report
    # damage type value present
    assert "INSTRUCTION_OVERRIDE" in report


def test_severity_breakdown():
    w = Warning(
        chunk_index=0,
        chunk_begin=0,
        chunk_end=100,
        start=0,
        end=10,
        threat="test",
        damage_types=[],
        certainty="SUSPICIOUS",
    )
    result = _make_result([w])
    report = format_report(result)
    assert "SUSPICIOUS: 1" in report
    assert "CLEARLY_MALICIOUS: 0" in report


def test_recommended_action_clearly_malicious():
    w = Warning(
        chunk_index=0,
        chunk_begin=0,
        chunk_end=100,
        start=0,
        end=10,
        threat="test",
        damage_types=[],
        certainty="CLEARLY_MALICIOUS",
    )
    result = _make_result([w])
    report = format_report(result)
    assert "REJECT" in report
