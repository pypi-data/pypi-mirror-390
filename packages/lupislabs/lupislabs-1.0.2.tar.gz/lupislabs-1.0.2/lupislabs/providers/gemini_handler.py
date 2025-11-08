from __future__ import annotations

import json
from typing import Any, Dict

from ..types import ProviderHandler, ProviderName


def _extract_text_from_parts(parts: Any) -> str:
    if not isinstance(parts, list):
        return ""
    texts: list[str] = []
    for part in parts:
        if isinstance(part, str):
            texts.append(part)
            continue
        if isinstance(part, dict):
            text_value = part.get("text")
            if isinstance(text_value, str):
                texts.append(text_value)
            elif isinstance(part.get("parts"), list):
                nested = _extract_text_from_parts(part["parts"])
                if nested:
                    texts.append(nested)
    return "".join(texts)


def _normalize_usage_metadata(usage_metadata: Any) -> dict[str, int] | None:
    if not isinstance(usage_metadata, dict):
        return None

    prompt_tokens = (
        usage_metadata.get("promptTokenCount")
        or usage_metadata.get("inputTokenCount")
        or usage_metadata.get("prompt_tokens")
        or usage_metadata.get("input_tokens")
        or 0
    )
    completion_tokens = (
        usage_metadata.get("candidatesTokenCount")
        or usage_metadata.get("completionTokenCount")
        or usage_metadata.get("outputTokenCount")
        or usage_metadata.get("responseTokenCount")
        or usage_metadata.get("completion_tokens")
        or usage_metadata.get("output_tokens")
        or 0
    )
    cache_tokens = (
        usage_metadata.get("cachedContentTokenCount")
        or usage_metadata.get("cacheTokenCount")
        or usage_metadata.get("cache_tokens")
        or 0
    )
    total_tokens = (
        usage_metadata.get("totalTokenCount")
        or usage_metadata.get("totalTokens")
        or usage_metadata.get("total_token_count")
        or usage_metadata.get("total_tokens")
        or prompt_tokens + completion_tokens + cache_tokens
    )

    return {
        "prompt_tokens": int(prompt_tokens),
        "completion_tokens": int(completion_tokens),
        "cache_tokens": int(cache_tokens),
        "total_tokens": int(total_tokens),
    }


def _extract_model_name(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None
    response_metadata = payload.get("responseMetadata")
    if isinstance(response_metadata, dict):
        response_model = response_metadata.get("modelVersion") or response_metadata.get("model")
    else:
        response_model = None
    return (
        payload.get("modelVersion")
        or payload.get("model")
        or response_model
        or payload.get("name")
    )


class GeminiHandler(ProviderHandler):
    provider: ProviderName = "gemini"

    def detect(self, url: str) -> bool:
        return (
            "generativelanguage.googleapis.com" in url
            or "aiplatform.googleapis.com" in url
            or "ai.googleusercontent.com" in url
            or "vertex.googleapis.com" in url
            or "api.google.com" in url
        )

    def is_streaming_chunk(self, text_chunk: str) -> bool:
        if not text_chunk:
            return False
        stripped = text_chunk.lstrip()
        return stripped.startswith("data: ") or "\ndata: " in text_chunk

    def accumulate_chunk(self, state: Any, text_chunk: str) -> Dict[str, Any]:
        next_state = state or {"__raw_chunks": [], "__aggregated_text": "", "__tool_calls": [], "__usage": None}
        next_state["__raw_chunks"].append(text_chunk)
        for line in text_chunk.split("\n"):
            if not line.startswith("data: "):
                continue
            payload = line[6:].strip()
            if not payload or payload == "[DONE]":
                continue
            try:
                json_data = json.loads(payload)
            except json.JSONDecodeError:
                continue

            model_name = _extract_model_name(json_data)
            if model_name:
                next_state["model"] = model_name

            usage_metadata = json_data.get("usageMetadata")
            if usage_metadata:
                next_state["__usage"] = _normalize_usage_metadata(usage_metadata) or usage_metadata

            candidates = json_data.get("candidates")
            if isinstance(candidates, list):
                for candidate in candidates:
                    parts = candidate.get("content", {}).get("parts")
                    if parts:
                        next_state["__aggregated_text"] += _extract_text_from_parts(parts)

                    if isinstance(parts, list):
                        for part in parts:
                            if not isinstance(part, dict):
                                continue
                            function_call = part.get("functionCall")
                            if not function_call:
                                continue
                            name = function_call.get("name")
                            if not name:
                                continue
                            next_state["__tool_calls"].append(
                                {
                                    "id": name,
                                    "name": name,
                                    "type": "function",
                                    "function": {
                                        "name": name,
                                        "arguments": json.dumps(function_call.get("args") or {}),
                                    },
                                }
                            )
        return {"state": next_state}

    def normalize_final(self, raw_body_text: str) -> Any:
        try:
            parsed = json.loads(raw_body_text)
        except json.JSONDecodeError:
            return raw_body_text

        aggregated_text = ""
        candidates = parsed.get("candidates")
        if isinstance(candidates, list):
            for candidate in candidates:
                parts = candidate.get("content", {}).get("parts")
                if parts:
                    aggregated_text += _extract_text_from_parts(parts)

        parsed["aggregatedText"] = aggregated_text

        normalized_usage = _normalize_usage_metadata(parsed.get("usageMetadata"))
        if normalized_usage:
            parsed["usage"] = normalized_usage

        model_name = _extract_model_name(parsed)
        if model_name:
            parsed["model"] = model_name
        return parsed
