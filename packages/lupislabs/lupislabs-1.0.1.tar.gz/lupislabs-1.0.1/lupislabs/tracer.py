from __future__ import annotations

import logging
from typing import Dict, Optional

from .http_interceptor import HttpInterceptor
from .trace_collector import TraceCollector
from .types import (
    ConversationContext,
    LupisConfig,
    LupisMetadata,
    MessageData,
    SensitiveDataFilter,
    ToolCallData,
)


class ConversationTracker:
    """Tracks conversation-level statistics to mirror the JS SDK behaviour."""

    def __init__(self) -> None:
        self._conversation_context: Optional[ConversationContext] = None
        self._message_counts = {"user": 0, "assistant": 0, "system": 0}
        self._tool_call_counts: Dict[str, int] = {}
        self._tool_result_counts: Dict[str, int] = {}

    def set_conversation_context(self, context: ConversationContext) -> None:
        self._conversation_context = context

    def clear_conversation_context(self) -> None:
        self._conversation_context = None
        self._message_counts = {"user": 0, "assistant": 0, "system": 0}
        self._tool_call_counts.clear()
        self._tool_result_counts.clear()

    def track_message(self, message: MessageData) -> None:
        if message.role not in self._message_counts:
            return
        self._message_counts[message.role] += 1

    def track_tool_call(self, tool_call: ToolCallData) -> None:
        current = self._tool_call_counts.get(tool_call.name, 0)
        self._tool_call_counts[tool_call.name] = current + 1

    def track_tool_result(self, tool_name: str) -> None:
        current = self._tool_result_counts.get(tool_name, 0)
        self._tool_result_counts[tool_name] = current + 1

    def get_conversation_data(self) -> Dict[str, object]:
        total_message_count = sum(self._message_counts.values())
        total_tool_call_count = sum(self._tool_call_counts.values())
        total_tool_result_count = sum(self._tool_result_counts.values())
        return {
            "context": self._conversation_context.to_dict() if self._conversation_context else None,
            "messageCounts": dict(self._message_counts),
            "totalMessageCount": total_message_count,
            "toolCallCounts": dict(self._tool_call_counts),
            "toolResultCounts": dict(self._tool_result_counts),
            "totalToolCallCount": total_tool_call_count,
            "totalToolResultCount": total_tool_result_count,
        }


class LupisTracer:
    """Coordinates HTTP interception and conversation tracking."""

    def __init__(self, config: LupisConfig) -> None:
        enabled = config.enabled is not False
        self._trace_collector = TraceCollector(
            endpoint=None,
            project_id=config.project_id,
            api_key=config.api_key,
            enabled=enabled,
        )
        filter_config = SensitiveDataFilter(
            filter_sensitive_data=config.filter_sensitive_data if config.filter_sensitive_data is not None else True,
            sensitive_data_patterns=config.sensitive_data_patterns or [],
            redaction_mode=config.redaction_mode or "mask",
        )
        self._http_interceptor = HttpInterceptor(
            trace_collector=self._trace_collector,
            project_id=config.project_id,
            sensitive_data_filter=filter_config,
        )
        self._conversation_tracker = ConversationTracker()

        if enabled:
            self._http_interceptor.start_intercepting()

    def set_chat_id(self, chat_id: str) -> None:
        self._http_interceptor.set_chat_id(chat_id)

    def clear_chat_id(self) -> None:
        self._http_interceptor.clear_chat_id()

    def set_metadata(self, metadata: LupisMetadata) -> None:
        self._http_interceptor.set_metadata(metadata)

    def clear_metadata(self) -> None:
        self._http_interceptor.clear_metadata()

    def set_conversation_context(self, context: ConversationContext) -> None:
        self._conversation_tracker.set_conversation_context(context)

    def track_message(self, message: MessageData) -> None:
        self._conversation_tracker.track_message(message)

    def track_tool_call(self, tool_call: ToolCallData) -> None:
        self._conversation_tracker.track_tool_call(tool_call)

    def track_tool_result(self, tool_name: str) -> None:
        self._conversation_tracker.track_tool_result(tool_name)

    def get_conversation_data(self) -> Dict[str, object]:
        return self._conversation_tracker.get_conversation_data()

    def shutdown(self) -> None:
        logging.info("[Lupis SDK] Stopping HTTP interception...")
        self._http_interceptor.stop_intercepting()
        logging.info("[Lupis SDK] Flushing traces...")
        self._trace_collector.force_flush()
        logging.info("[Lupis SDK] Shutdown complete")

