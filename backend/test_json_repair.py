"""Quick smoke test for the JSON repair fixes."""
from app.validation.json_repair import repair_json

def test_normal_json():
    raw = '{"app_name": "Todo App", "features": ["auth"]}'
    parsed, repaired = repair_json(raw)
    assert parsed["app_name"] == "Todo App"
    assert not repaired
    print("PASS: normal JSON")

def test_escaped_single_quotes():
    # Simulates LLM producing \' inside double-quoted strings
    raw = '{"note": "It\\\'s a test"}'
    parsed, repaired = repair_json(raw)
    assert parsed["note"] == "It's a test"
    assert repaired
    print("PASS: escaped single quotes")

def test_single_quote_delimited():
    raw = "{'app_name': 'Todo', 'v': 1}"
    parsed, repaired = repair_json(raw)
    assert parsed["app_name"] == "Todo"
    assert repaired
    print("PASS: single-quote delimited")

def test_trailing_comma():
    raw = '{"a": 1, "b": [1, 2,]}'
    parsed, repaired = repair_json(raw)
    assert parsed["b"] == [1, 2]
    assert repaired
    print("PASS: trailing comma")

def test_double_quoted_with_embedded_singles():
    # Double-quoted JSON with single quotes in values — must NOT mangle
    raw = '{"note": "don\'t touch this", "name": "O\'Brien"}'
    parsed, repaired = repair_json(raw)
    assert "don't" in parsed["note"]
    assert "O'Brien" in parsed["name"]
    print("PASS: embedded singles in double-quoted JSON")

if __name__ == "__main__":
    test_normal_json()
    test_escaped_single_quotes()
    test_single_quote_delimited()
    test_trailing_comma()
    test_double_quoted_with_embedded_singles()
    print("\nAll JSON repair tests passed!")
