from snuffer.sanitizer import strip_brackets


def test_strips_simple_bracket():
    text = "hello ⟪SNUF:9f3a2b1c:B⟫ world ⟪SNUF:9f3a2b1c:E⟫"
    assert strip_brackets(text) == "hello  world "


def test_strips_multiple_keys():
    text = "⟪SNUF:aaaaaaaa:B⟫ foo ⟪SNUF:bbbbbbbb:B⟫ bar ⟪SNUF:aaaaaaaa:E⟫"
    result = strip_brackets(text)
    assert "⟪SNUF:" not in result
    assert "foo" in result
    assert "bar" in result


def test_recursive_nested_forgery():
    # Attacker nests to reconstruct after one removal
    text = "⟪SNUF:9f3a⟪SNUF:9f3a2b1c:B⟫2b1c:B⟫ evil ⟪SNUF:9f3a2b1c:E⟫"
    result = strip_brackets(text)
    assert "⟪SNUF:" not in result


def test_idempotent_on_clean_text():
    text = "The quick brown fox"
    assert strip_brackets(text) == text


def test_empty_string():
    assert strip_brackets("") == ""
