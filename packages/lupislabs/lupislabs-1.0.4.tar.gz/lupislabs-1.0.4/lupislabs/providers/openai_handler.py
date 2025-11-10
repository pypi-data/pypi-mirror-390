from __future__ import annotations

import json
from typing import Any, Dict

from ..types import ProviderHandler, ProviderName


class OpenAIHandler(ProviderHandler):
    provider: ProviderName = "openai"

    def detect(self, url: str) -> bool:
        return "api.openai.com" in url

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
            if payload == "[DONE]":
                continue
            try:
                json_data = json.loads(payload)
            except json.JSONDecodeError:
                continue
            if json_data.get("model"):
                next_state["model"] = json_data["model"]
            choices = json_data.get("choices")
            if isinstance(choices, list):
                for choice in choices:
                    delta = choice.get("delta", {})
                    if delta.get("content"):
                        next_state["__aggregated_text"] += delta["content"]
                    tool_calls = delta.get("tool_calls")
                    if isinstance(tool_calls, list):
                        next_state["__tool_calls"].extend(tool_calls)
            usage = json_data.get("usage")
            if usage:
                next_state["__usage"] = usage
        return {"state": next_state}

    def normalize_final(self, raw_body_text: str) -> Any:
        try:
            parsed = json.loads(raw_body_text)
        except json.JSONDecodeError:
            return raw_body_text
        aggregated_text = ""
        choices = parsed.get("choices")
        if isinstance(choices, list) and choices:
            message = choices[0].get("message", {})
            aggregated_text = message.get("content", "") or ""
        parsed["aggregatedText"] = aggregated_text
        return parsed
