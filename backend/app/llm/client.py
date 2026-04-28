"""Unified LLM client abstracting GroqCloud and OpenAI APIs.

Features:
    - temperature=0, JSON mode enforced
    - Token budget enforcement per stage
    - Retry with exponential backoff (max 2 retries)
    - Response parsing + JSON extraction
    - Cost tracking (input/output tokens → USD estimate)
"""

from __future__ import annotations

import asyncio
import time
import logging
from typing import Any

from app.core.config import settings
from app.validation.json_repair import repair_json

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cost per 1M tokens (approximate, for tracking only)
# ---------------------------------------------------------------------------
COST_TABLE: dict[str, dict[str, float]] = {
    "groq": {"input": 0.59, "output": 0.79},  # Llama3-70b on GroqCloud
    "openai": {"input": 2.5, "output": 10.0},  # GPT-4o
}

# Token budget per stage
TOKEN_BUDGETS: dict[str, int] = {
    "stage1_intent": 1000,
    "stage2_design": 4000,
    "stage3_db": 4000,
    "stage3_api": 4000,
    "stage3_ui": 4000,
    "stage3_auth": 2000,
    "stage4_repair": 3000,
}


class LLMResponse:
    """Wrapper for LLM response with metadata."""

    def __init__(
        self,
        content: str,
        parsed: dict[str, Any] | None,
        input_tokens: int,
        output_tokens: int,
        latency_ms: int,
        cost_usd: float,
        was_repaired: bool = False,
    ) -> None:
        self.content = content
        self.parsed = parsed
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.latency_ms = latency_ms
        self.cost_usd = cost_usd
        self.was_repaired = was_repaired


class LLMClient:
    """Unified client for GroqCloud/OpenAI with JSON mode and retry logic."""

    def __init__(self, provider: str | None = None) -> None:
        self.provider: str = provider or settings.LLM_PROVIDER
        self._groq_client: Any = None
        self._openai_client: Any = None

        if self.provider == "groq":
            import openai as openai_sdk  # type: ignore[import-untyped]
            self._groq_client = openai_sdk.OpenAI(
                api_key=settings.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1",
            )
        elif self.provider == "openai":
            import openai  # type: ignore[import-untyped]
            self._openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")

    async def generate(
        self,
        prompt: str,
        stage: str = "default",
        max_retries: int = 6,
    ) -> LLMResponse:
        """Generate a JSON response from the LLM.

        Args:
            prompt: The full prompt string (system + user content combined).
            stage: Pipeline stage name (for token budget enforcement).
            max_retries: Max retry attempts on failure.

        Returns:
            LLMResponse with parsed JSON and metadata.
        """
        max_tokens = TOKEN_BUDGETS.get(stage, 1500)
        last_error: Exception | None = None

        for attempt in range(max_retries + 1):
            try:
                start = time.time()

                if self.provider == "groq":
                    content, input_tok, output_tok = self._call_groq(
                        prompt, max_tokens
                    )
                else:
                    content, input_tok, output_tok = self._call_openai(
                        prompt, max_tokens
                    )

                latency_ms = int((time.time() - start) * 1000)

                # Calculate cost
                cost_rates = COST_TABLE.get(self.provider, {"input": 0.0, "output": 0.0})
                cost_usd = (
                    (input_tok * cost_rates["input"] / 1_000_000)
                    + (output_tok * cost_rates["output"] / 1_000_000)
                )

                # Parse JSON (with repair)
                parsed: dict[str, Any] | None = None
                was_repaired = False
                try:
                    parsed, was_repaired = repair_json(content)
                except ValueError:
                    parsed = None
                    was_repaired = False

                return LLMResponse(
                    content=content,
                    parsed=parsed,
                    input_tokens=input_tok,
                    output_tokens=output_tok,
                    latency_ms=latency_ms,
                    cost_usd=round(cost_usd, 6),
                    was_repaired=was_repaired,
                )

            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    wait = float(3 ** attempt)  # Exponential backoff: 1s, 3s, 9s, 27s
                    
                    import re
                    err_str = str(e)
                    match = re.search(r"try again in ([\d\.]+)s", err_str)
                    if match:
                        wait = float(match.group(1)) + 1.0
                        
                    logger.warning(
                        f"LLM call failed (attempt {attempt + 1}/{max_retries + 1}), "
                        f"retrying in {wait}s: {e}"
                    )
                    await asyncio.sleep(wait)

        raise RuntimeError(
            f"LLM call failed after {max_retries + 1} attempts: {last_error}"
        )

    def _call_groq(
        self, prompt: str, max_tokens: int
    ) -> tuple[str, int, int]:
        """Call GroqCloud API (OpenAI-compatible)."""
        if self._groq_client is None:
            raise RuntimeError("Groq client not initialized")
        response = self._groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=max_tokens,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You output only valid JSON."},
                {"role": "user", "content": prompt},
            ],
        )
        content: str = response.choices[0].message.content or ""
        finish_reason = response.choices[0].finish_reason

        # If the model was cut off, the JSON is almost certainly incomplete
        if finish_reason != "stop":
            logger.warning(
                f"Groq response truncated (finish_reason={finish_reason}, "
                f"content_len={len(content)}). Will retry."
            )
            raise RuntimeError(
                f"Groq response truncated: finish_reason={finish_reason}"
            )

        usage = response.usage
        input_tok: int = usage.prompt_tokens if usage else 0
        output_tok: int = usage.completion_tokens if usage else 0
        return content, input_tok, output_tok

    def _call_openai(
        self, prompt: str, max_tokens: int
    ) -> tuple[str, int, int]:
        """Call OpenAI API with JSON mode."""
        if self._openai_client is None:
            raise RuntimeError("OpenAI client not initialized")
        response = self._openai_client.chat.completions.create(
            model="gpt-4o",
            max_tokens=max_tokens,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You output only valid JSON."},
                {"role": "user", "content": prompt},
            ],
        )
        content: str = response.choices[0].message.content or ""
        usage = response.usage
        input_tok: int = usage.prompt_tokens if usage else 0
        output_tok: int = usage.completion_tokens if usage else 0
        return content, input_tok, output_tok


# ---------------------------------------------------------------------------
# Singleton client instance
# ---------------------------------------------------------------------------

_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    """Get or create the singleton LLM client."""
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
