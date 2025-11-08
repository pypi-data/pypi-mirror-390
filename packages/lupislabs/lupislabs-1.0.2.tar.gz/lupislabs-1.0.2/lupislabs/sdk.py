from __future__ import annotations

import asyncio
import atexit
import inspect
import logging
import os
from typing import Any, Awaitable, Callable, Dict, Optional, TypeVar, Union, cast

from .tracer import LupisTracer
from .types import (
    ConversationContext,
    LupisBlockOptions,
    LupisConfig,
    LupisMetadata,
    MessageData,
    ToolCallData,
)

T = TypeVar("T")

_global_instance: Optional["LupisSDK"] = None


def _is_dev_mode(config: LupisConfig) -> bool:
    if config.enabled is False:
        return False
    if config.enabled is True:
        return True

    env_flag = os.getenv("LUPIS_SDK_ENABLED")
    if env_flag == "true":
        return True
    if env_flag == "false":
        return False

    node_env = os.getenv("NODE_ENV")
    if node_env:
        return node_env.lower() != "production"

    return False


class _NoopTracer:
    def set_metadata(self, _: LupisMetadata) -> None:
        pass

    def clear_metadata(self) -> None:
        pass

    def set_chat_id(self, _: str) -> None:
        pass

    def clear_chat_id(self) -> None:
        pass

    def set_conversation_context(self, _: ConversationContext) -> None:
        pass

    def track_message(self, _: MessageData) -> None:
        pass

    def track_tool_call(self, _: ToolCallData) -> None:
        pass

    def track_tool_result(self, _: str) -> None:
        pass

    def get_conversation_data(self) -> Dict[str, Any]:
        return {
            "context": None,
            "messageCounts": {"user": 0, "assistant": 0, "system": 0},
            "totalMessageCount": 0,
            "toolCallCounts": {},
            "toolResultCounts": {},
            "totalToolCallCount": 0,
            "totalToolResultCount": 0,
        }

    def shutdown(self) -> None:
        pass


class LupisSDK:
    """Python implementation of the Lupis SDK mirroring the JS behaviour."""

    def __init__(self, config: LupisConfig):
        self._config = config
        self._enabled = _is_dev_mode(config)
        normalized_config = LupisConfig(
            project_id=config.project_id,
            api_key=config.api_key,
            enabled=self._enabled,
            otlp_endpoint=config.otlp_endpoint,
            service_name=config.service_name,
            service_version=config.service_version,
            filter_sensitive_data=config.filter_sensitive_data,
            sensitive_data_patterns=config.sensitive_data_patterns,
            redaction_mode=config.redaction_mode,
        )
        self._tracer = LupisTracer(normalized_config) if self._enabled else _NoopTracer()
        self._global_metadata: LupisMetadata = {}
        self._register_shutdown_hook()

    @classmethod
    def init(cls, config: LupisConfig) -> "LupisSDK":
        global _global_instance  # noqa: PLW0603
        if _global_instance is not None:
            logging.warning("[Lupis SDK] Already initialized. Returning existing instance.")
            return _global_instance

        dev_mode = _is_dev_mode(config)
        if not dev_mode:
            logging.warning(
                "[Lupis SDK] SDK is disabled in production mode. "
                "Set enabled=True in config or LUPIS_SDK_ENABLED=true to override."
            )
            disabled_config = LupisConfig(
                project_id=config.project_id,
                api_key=config.api_key,
                enabled=False,
                otlp_endpoint=config.otlp_endpoint,
                service_name=config.service_name,
                service_version=config.service_version,
                filter_sensitive_data=config.filter_sensitive_data,
                sensitive_data_patterns=config.sensitive_data_patterns,
                redaction_mode=config.redaction_mode,
            )
            _global_instance = cls(disabled_config)
            return _global_instance
        _global_instance = cls(config)
        return _global_instance

    @classmethod
    def get_instance(cls) -> Optional["LupisSDK"]:
        return _global_instance

    def is_enabled(self) -> bool:
        return self._enabled

    def set_metadata(self, metadata: LupisMetadata) -> None:
        if not metadata:
            return
        self._global_metadata.update(metadata)
        self._tracer.set_metadata(dict(self._global_metadata))

    def get_metadata(self) -> LupisMetadata:
        return dict(self._global_metadata)

    def clear_metadata(self) -> None:
        self._global_metadata.clear()
        self._tracer.clear_metadata()

    def set_chat_id(self, chat_id: str) -> None:
        self._tracer.set_chat_id(chat_id)

    def clear_chat_id(self) -> None:
        self._tracer.clear_chat_id()

    def set_conversation_context(self, context: ConversationContext) -> None:
        self._tracer.set_conversation_context(context)

    def track_message(self, message: MessageData) -> None:
        self._tracer.track_message(message)

    def track_tool_call(self, tool_call: ToolCallData) -> None:
        self._tracer.track_tool_call(tool_call)

    def track_tool_result(self, tool_name: str) -> None:
        self._tracer.track_tool_result(tool_name)

    def get_conversation_data(self) -> Dict[str, Any]:
        return self._tracer.get_conversation_data()

    async def run(
        self,
        fn: Callable[[], Union[T, Awaitable[T]]],
        options: Optional[LupisBlockOptions] = None,
    ) -> T:
        options = options or LupisBlockOptions()
        if options.chat_id:
            self.set_chat_id(options.chat_id)

        try:
            result = fn()
            if inspect.isawaitable(result):
                return cast(T, await result)
            return cast(T, result)
        finally:
            if options.chat_id:
                self.clear_chat_id()

    async def shutdown(self) -> None:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._tracer.shutdown)

    def _register_shutdown_hook(self) -> None:
        if not self._enabled:
            return

        def _safe_shutdown() -> None:
            try:
                self._tracer.shutdown()
            except Exception:  # pragma: no cover - best effort at process exit
                logging.exception("[Lupis SDK] Error while shutting down during interpreter exit")

        atexit.register(_safe_shutdown)
