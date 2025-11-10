from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Protocol, Union


LupisMetadata = Dict[str, Union[str, int, float, bool, None]]


@dataclass
class LupisConfig:
    project_id: str
    api_key: Optional[str] = None
    enabled: Optional[bool] = None
    otlp_endpoint: Optional[str] = None  # Backwards compatibility with previous versions
    service_name: Optional[str] = None
    service_version: Optional[str] = None
    filter_sensitive_data: Optional[bool] = None
    sensitive_data_patterns: Optional[List[str]] = None
    redaction_mode: Optional[Literal["mask", "remove", "hash"]] = None


@dataclass
class LupisBlockOptions:
    chat_id: Optional[str] = None
    name: Optional[str] = None
    metadata: Optional[LupisMetadata] = None
    capture_http: bool = True
    capture_console: bool = False


@dataclass
class ConversationContext:
    chat_id: str
    session_id: Optional[str] = None
    thread_id: Optional[str] = None
    user_id: str = ""
    user_name: Optional[str] = None
    organization_id: Optional[str] = None
    organization_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chatId": self.chat_id,
            "sessionId": self.session_id,
            "threadId": self.thread_id,
            "userId": self.user_id,
            "userName": self.user_name,
            "organizationId": self.organization_id,
            "organizationName": self.organization_name,
        }


ProviderName = Literal["openai", "claude", "gemini", "cohere", "huggingface", "google", "unknown"]


@dataclass
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_tokens: int = 0
    total_tokens: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cache_tokens": self.cache_tokens,
            "total_tokens": self.total_tokens,
        }


@dataclass
class CostBreakdown:
    input_cost: float = 0.0
    output_cost: float = 0.0
    cache_cost: float = 0.0
    total_cost: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_cost": self.input_cost,
            "output_cost": self.output_cost,
            "cache_cost": self.cache_cost,
            "total_cost": self.total_cost,
        }


@dataclass
class TraceData:
    id: str
    project_id: str
    timestamp: int
    type: Literal["http_request", "tool_call", "message"] = "http_request"
    duration: Optional[int] = None
    input: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    chat_id: Optional[str] = None
    session_id: Optional[str] = None
    thread_id: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    organization_id: Optional[str] = None
    organization_name: Optional[str] = None
    token_usage: Optional[TokenUsage] = None
    cost_breakdown: Optional[CostBreakdown] = None
    model: Optional[str] = None
    user_message_count: Optional[int] = None
    assistant_message_count: Optional[int] = None
    total_message_count: Optional[int] = None
    tool_call_count: Optional[int] = None
    tool_result_count: Optional[int] = None
    tool: Optional[Dict[str, Any]] = None
    metadata: Optional[LupisMetadata] = None
    tags: Optional[List[str]] = None


@dataclass
class NormalizedStreamingResult:
    type: Literal["streaming_response"] = "streaming_response"
    provider: ProviderName = "unknown"
    model: Optional[str] = None
    aggregated_text: Optional[str] = None
    data: Optional[List[str]] = None
    tool_calls: Optional[List[Any]] = None
    usage: Optional[Any] = None
    content_type: Optional[str] = None
    total_chunks: Optional[int] = None
    total_length: Optional[int] = None
    is_complete: Optional[bool] = None


class ProviderHandler(Protocol):
    provider: ProviderName

    def detect(self, url: str) -> bool:
        ...

    def is_streaming_chunk(self, text_chunk: str) -> bool:
        ...

    def accumulate_chunk(self, state: Any, text_chunk: str) -> Dict[str, Any]:
        ...

    def normalize_final(self, raw_body_text: str) -> Any:
        ...


@dataclass
class SensitiveDataFilter:
    filter_sensitive_data: bool = True
    sensitive_data_patterns: Optional[List[str]] = None
    redaction_mode: Literal["mask", "remove", "hash"] = "mask"


class LupisInterceptorLike(Protocol):
    def start_intercepting(self) -> None:
        ...

    def stop_intercepting(self) -> None:
        ...

    def set_chat_id(self, chat_id: str) -> None:
        ...

    def clear_chat_id(self) -> None:
        ...
