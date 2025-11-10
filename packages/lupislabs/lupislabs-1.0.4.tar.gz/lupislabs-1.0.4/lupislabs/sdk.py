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
)

T = TypeVar("T")

_global_instance: Optional["LupisLabs"] = None


def _is_enabled() -> bool:
    env_flag = os.getenv("LUPIS_SDK_ENABLED")
    return env_flag == "true"


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


class LupisLabs:
    """Python implementation of the LupisLabs SDK mirroring the JS behaviour."""

    def __init__(self, config: LupisConfig):
        self._config = config
        self._enabled = _is_enabled()
        self._tracer = LupisTracer(config) if self._enabled else _NoopTracer()
        self._global_metadata: LupisMetadata = {}
        self._register_shutdown_hook()

    @classmethod
    def init(cls, config: LupisConfig) -> "LupisLabs":
        global _global_instance  # noqa: PLW0603
        if _global_instance is not None:
            logging.warning("[LupisLabs SDK] Already initialized. Returning existing instance.")
            return _global_instance

        if not _is_enabled():
            logging.warning(
                "[LupisLabs SDK] SDK is disabled. "
                "Set LUPIS_SDK_ENABLED=true environment variable to enable."
            )
        _global_instance = cls(config)
        return _global_instance

    @classmethod
    def get_instance(cls) -> Optional["LupisLabs"]:
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
                logging.exception(
                    "[LupisLabs SDK] Error while shutting down during interpreter exit"
                )

        atexit.register(_safe_shutdown)
