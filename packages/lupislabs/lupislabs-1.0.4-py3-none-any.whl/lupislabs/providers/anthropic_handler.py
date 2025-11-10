from __future__ import annotations

import json
from typing import Any, Dict

from ..types import ProviderHandler, ProviderName


class AnthropicHandler(ProviderHandler):
    provider: ProviderName = "claude"

    def detect(self, url: str) -> bool:
        return "api.anthropic.com" in url

    def is_streaming_chunk(self, text_chunk: str) -> bool:
        if not text_chunk:
            return False
        stripped = text_chunk.lstrip()
        return stripped.startswith("event: ") or stripped.startswith("data: ") or "\ndata: " in text_chunk

    def accumulate_chunk(self, state: Any, text_chunk: str) -> Dict[str, Any]:
        next_state = state or {"__raw_chunks": [], "__aggregated_text": "", "__tool_calls": [], "__usage": None}
        next_state["__raw_chunks"].append(text_chunk)
        for line in text_chunk.split("\n"):
            if not line.startswith("data: "):
                continue
            try:
                json_data = json.loads(line[6:])
            except json.JSONDecodeError:
                continue
            if json_data.get("message", {}).get("model"):
                next_state["model"] = json_data["message"]["model"]
            elif json_data.get("model"):
                next_state["model"] = json_data["model"]
            delta = json_data.get("delta", {})
            if delta.get("text"):
                next_state["__aggregated_text"] += delta["text"]
            if json_data.get("type") == "tool_use":
                next_state["__tool_calls"].append(
                    {
                        "id": json_data.get("id"),
                        "name": json_data.get("name"),
                        "type": "function",
                        "function": {
                            "name": json_data.get("name"),
                            "arguments": json.dumps(json_data.get("input") or {}),
                        },
                    }
                )
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
        content = parsed.get("content")
        if isinstance(content, list) and content:
            aggregated_text = content[0].get("text", "") or ""
        parsed["aggregatedText"] = aggregated_text
        return parsed
