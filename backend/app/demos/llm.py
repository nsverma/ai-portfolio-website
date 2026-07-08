"""Optional LLM upgrade for the agent demos.

Every agent works fully without an LLM (retrieval, classifiers, rules).
If ANTHROPIC_API_KEY is set, generation steps are upgraded to Claude via the
official Anthropic SDK. Model can be overridden with DEMO_LLM_MODEL.
"""

import os
from functools import lru_cache

MODEL = os.environ.get("DEMO_LLM_MODEL", "claude-opus-4-8")


@lru_cache(maxsize=1)
def _client():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic

        return anthropic.Anthropic()
    except Exception:
        return None


def available() -> bool:
    return _client() is not None


def generate(system: str, prompt: str, max_tokens: int = 600) -> str | None:
    """Returns Claude's answer, or None when no key is configured / call fails."""
    client = _client()
    if client is None:
        return None
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        if response.stop_reason == "refusal":
            return None
        return next((b.text for b in response.content if b.type == "text"), None)
    except Exception:
        return None
