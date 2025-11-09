from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


@dataclass
class Pricing:
    input_per_1k: float
    output_per_1k: float
    cache_per_1k: float = 0.0


PRICING_TABLE: Dict[str, Dict[str, Pricing]] = {
    "openai": {
        "gpt-4": Pricing(0.03, 0.06),
        "gpt-4-turbo": Pricing(0.01, 0.03),
        "gpt-3.5-turbo": Pricing(0.0015, 0.002),
        "default": Pricing(0.03, 0.06),
    },
    "claude": {
        "claude-3-opus": Pricing(0.015, 0.075),
        "claude-3-sonnet": Pricing(0.003, 0.015),
        "claude-3-haiku": Pricing(0.00025, 0.00125),
        "default": Pricing(0.003, 0.015),
    },
    "gemini": {
        "gemini-pro": Pricing(0.0005, 0.0015),
        "default": Pricing(0.0005, 0.0015),
    },
    "google": {
        "gemini-pro": Pricing(0.0005, 0.0015),
        "default": Pricing(0.0005, 0.0015),
    },
}

DEFAULT_PRICING = Pricing(0.001, 0.002)


def get_pricing(provider: str, model: Optional[str]) -> Pricing:
    provider_pricing = PRICING_TABLE.get(provider, {})
    if not provider_pricing:
        return DEFAULT_PRICING

    if model and model in provider_pricing:
        return provider_pricing[model]

    return provider_pricing.get("default", DEFAULT_PRICING)


def calculate_cost(token_usage: Any, provider: str, model: Optional[str]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Normalize token usage data and produce a cost breakdown."""
    if not token_usage:
        return {}, {}

    input_tokens = (
        token_usage.get("prompt_tokens")
        if isinstance(token_usage, dict)
        else getattr(token_usage, "prompt_tokens", 0)
    )
    if input_tokens is None:
        input_tokens = (
            token_usage.get("input_tokens")
            if isinstance(token_usage, dict)
            else getattr(token_usage, "input_tokens", 0)
        )

    output_tokens = (
        token_usage.get("completion_tokens")
        if isinstance(token_usage, dict)
        else getattr(token_usage, "completion_tokens", 0)
    )
    if output_tokens is None:
        output_tokens = (
            token_usage.get("output_tokens")
            if isinstance(token_usage, dict)
            else getattr(token_usage, "output_tokens", 0)
        )

    cache_tokens = (
        token_usage.get("cache_tokens")
        if isinstance(token_usage, dict)
        else getattr(token_usage, "cache_tokens", 0)
    ) or 0

    input_tokens = int(input_tokens or 0)
    output_tokens = int(output_tokens or 0)
    cache_tokens = int(cache_tokens or 0)
    total_tokens = input_tokens + output_tokens + cache_tokens

    pricing = get_pricing(provider, model)
    input_cost = (input_tokens / 1000.0) * pricing.input_per_1k
    output_cost = (output_tokens / 1000.0) * pricing.output_per_1k
    cache_cost = (cache_tokens / 1000.0) * pricing.cache_per_1k
    total_cost = input_cost + output_cost + cache_cost

    normalized_usage = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_tokens": cache_tokens,
        "total_tokens": total_tokens,
    }

    cost_breakdown = {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "cache_cost": cache_cost,
        "total_cost": total_cost,
    }

    return normalized_usage, cost_breakdown
