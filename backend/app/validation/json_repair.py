"""JSON repair utilities for fixing malformed LLM output.

LLMs frequently produce almost-valid JSON with common issues like:
- Markdown fences wrapping the JSON
- Trailing commas
- Single-quoted strings
- Unquoted keys
- Truncated output (missing closing braces)

This module repairs these issues deterministically before attempting
to parse the JSON.
"""

from __future__ import annotations

import json
import re
from typing import Any


def repair_json(raw: str) -> tuple[dict[str, Any], bool]:
    """Attempt to repair and parse malformed JSON.

    Args:
        raw: Raw string output from LLM (may contain markdown fences, etc.)

    Returns:
        Tuple of (parsed_dict, was_repaired).
        was_repaired is True if any fixes were applied.

    Raises:
        ValueError: If the JSON cannot be repaired.
    """
    original = raw
    text = raw.strip()
    repaired = False

    # --- Step 1: Strip markdown code fences ---
    text, did_strip = _strip_markdown_fences(text)
    repaired = repaired or did_strip

    # --- Step 2: Strip leading/trailing prose ---
    text, did_strip = _extract_json_object(text)
    repaired = repaired or did_strip

    # --- Step 3: Fix trailing commas ---
    text, did_fix = _fix_trailing_commas(text)
    repaired = repaired or did_fix

    # --- Step 4: Fix invalid backslash-escaped single quotes ---
    text, did_fix = _fix_escaped_single_quotes(text)
    repaired = repaired or did_fix

    # --- Step 5: Fix single-quoted strings (only if JSON still fails) ---
    text, did_fix = _fix_single_quotes(text)
    repaired = repaired or did_fix

    # --- Step 6: Try parsing ---
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed, repaired
        raise ValueError(f"Expected JSON object, got {type(parsed).__name__}")
    except json.JSONDecodeError:
        pass

    # --- Step 7: Try truncating at last valid closing brace ---
    text_trunc, did_trunc = _truncate_to_last_brace(text)
    if did_trunc:
        try:
            parsed = json.loads(text_trunc)
            if isinstance(parsed, dict):
                return parsed, True
        except json.JSONDecodeError:
            pass

    raise ValueError(
        f"Cannot repair JSON. First 200 chars: {original[:200]}"
    )


def _strip_markdown_fences(text: str) -> tuple[str, bool]:
    """Remove ```json ... ``` or ``` ... ``` fences."""
    # Pattern: ```json\n ... \n```  or ```\n ... \n```
    pattern = r"^```(?:json|JSON)?\s*\n(.*?)```\s*$"
    match = re.match(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip(), True
    return text, False


def _extract_json_object(text: str) -> tuple[str, bool]:
    """Extract the first JSON object from text that may have prose around it."""
    # Find the first { and last }
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
        extracted = text[first_brace : last_brace + 1]
        if extracted != text:
            return extracted, True
    return text, False


def _fix_trailing_commas(text: str) -> tuple[str, bool]:
    """Remove trailing commas before } or ]."""
    # Match comma followed by optional whitespace then } or ]
    fixed = re.sub(r",(\s*[}\]])", r"\1", text)
    return fixed, fixed != text


def _fix_escaped_single_quotes(text: str) -> tuple[str, bool]:
    """Fix invalid backslash-escaped single quotes inside JSON strings.

    LLMs frequently produce \\' inside double-quoted JSON strings,
    but \\' is NOT a valid JSON escape sequence.  Single quotes are
    perfectly legal inside double-quoted strings, so we simply
    remove the backslash:  \\'  →  '
    """
    if "\\" not in text or "'" not in text:
        return text, False
    fixed = text.replace("\\'", "'")
    return fixed, fixed != text


def _fix_single_quotes(text: str) -> tuple[str, bool]:
    """Replace single-quoted strings with double-quoted strings.

    Only applied when the text appears to be single-quote-delimited JSON
    (no double-quoted keys found).  If the text already uses double quotes
    for keys, we leave it alone to avoid mangling embedded single quotes.
    """
    if "'" not in text:
        return text, False

    # If we already see double-quoted keys, the JSON structure uses
    # double quotes — any remaining single quotes are literal characters
    # inside string values and should NOT be converted.
    if re.search(r'"[^"]+"\s*:', text):
        return text, False

    # No double-quoted keys found → the JSON is likely single-quote delimited
    fixed = re.sub(r"'([^']*?)'", r'"\1"', text)
    return fixed, fixed != text


def _truncate_to_last_brace(text: str) -> tuple[str, bool]:
    """Try to balance braces by truncating at the last valid closing point."""
    depth = 0
    last_valid_pos = -1

    i = 0
    in_string = False
    escape_next = False

    while i < len(text):
        ch = text[i]

        if escape_next:
            escape_next = False
            i += 1
            continue

        if ch == "\\":
            escape_next = True
            i += 1
            continue

        if ch == '"':
            in_string = not in_string
            i += 1
            continue

        if in_string:
            i += 1
            continue

        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                last_valid_pos = i

        i += 1

    if last_valid_pos > 0 and last_valid_pos < len(text) - 1:
        return text[: last_valid_pos + 1], True

    return text, False
