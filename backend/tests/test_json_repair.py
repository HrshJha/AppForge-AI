"""Tests for JSON repair utilities."""

import pytest
from app.validation.json_repair import repair_json


class TestStripMarkdownFences:
    def test_json_fence(self):
        raw = '```json\n{"key": "value"}\n```'
        result, repaired = repair_json(raw)
        assert result == {"key": "value"}
        assert repaired is True

    def test_plain_fence(self):
        raw = '```\n{"key": "value"}\n```'
        result, repaired = repair_json(raw)
        assert result == {"key": "value"}
        assert repaired is True

    def test_no_fence(self):
        raw = '{"key": "value"}'
        result, repaired = repair_json(raw)
        assert result == {"key": "value"}
        assert repaired is False


class TestTrailingCommas:
    def test_trailing_comma_in_object(self):
        raw = '{"a": 1, "b": 2,}'
        result, repaired = repair_json(raw)
        assert result == {"a": 1, "b": 2}
        assert repaired is True

    def test_trailing_comma_in_array(self):
        raw = '{"items": [1, 2, 3,]}'
        result, repaired = repair_json(raw)
        assert result == {"items": [1, 2, 3]}
        assert repaired is True

    def test_nested_trailing_commas(self):
        raw = '{"a": {"b": 1,}, "c": [1,],}'
        result, repaired = repair_json(raw)
        assert result == {"a": {"b": 1}, "c": [1]}
        assert repaired is True


class TestSingleQuotes:
    def test_single_quoted_keys_and_values(self):
        raw = "{'key': 'value'}"
        result, repaired = repair_json(raw)
        assert result == {"key": "value"}
        assert repaired is True


class TestProseStripping:
    def test_prose_before_json(self):
        raw = 'Here is the JSON output:\n{"key": "value"}'
        result, repaired = repair_json(raw)
        assert result == {"key": "value"}
        assert repaired is True

    def test_prose_after_json(self):
        raw = '{"key": "value"}\nLet me know if you need anything else.'
        result, repaired = repair_json(raw)
        assert result == {"key": "value"}
        assert repaired is True


class TestTruncation:
    def test_truncated_json_extra_text(self):
        raw = '{"key": "value"} extra garbage'
        result, repaired = repair_json(raw)
        assert result == {"key": "value"}
        assert repaired is True


class TestInvalidJson:
    def test_completely_invalid(self):
        raw = "This is not JSON at all, no braces here"
        with pytest.raises(ValueError, match="Cannot repair JSON"):
            repair_json(raw)

    def test_empty_string(self):
        with pytest.raises(ValueError):
            repair_json("")


class TestComplexRepair:
    def test_combined_issues(self):
        """Markdown fence + trailing comma + prose."""
        raw = """Here is your config:
```json
{
  "app_name": "TestApp",
  "features": ["login", "dashboard",],
}
```
Let me know if this works!"""
        result, repaired = repair_json(raw)
        assert result["app_name"] == "TestApp"
        assert result["features"] == ["login", "dashboard"]
        assert repaired is True
