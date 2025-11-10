from __future__ import annotations

import json
import logging
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional, Set

import requests

from .endpoints import DEFAULT_TRACES_ENDPOINT


@dataclass
class HttpTrace:
    id: str
    project_id: str
    timestamp: int
    type: str = "http_request"
    duration: Optional[int] = None
    url: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    provider: Optional[str] = None
    request_headers: Optional[Dict[str, str]] = None
    response_headers: Optional[Dict[str, str]] = None
    token_usage: Optional[Dict[str, Any]] = None
    cost_breakdown: Optional[Dict[str, Any]] = None
    model: Optional[str] = None
    request_body: Optional[str] = None
    response_body: Optional[str] = None
    chat_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> Dict[str, Any]:
        payload = asdict(self)
        cleaned = {key: value for key, value in payload.items() if value is not None and key != "extra"}

        snake_to_camel = {
            "project_id": "projectId",
            "status_code": "statusCode",
            "request_headers": "requestHeaders",
            "response_headers": "responseHeaders",
            "token_usage": "tokenUsage",
            "cost_breakdown": "costBreakdown",
            "request_body": "requestBody",
            "response_body": "responseBody",
            "chat_id": "chatId",
        }
        for snake_key, camel_key in snake_to_camel.items():
            if snake_key in cleaned:
                cleaned[camel_key] = cleaned.pop(snake_key)

        if self.extra:
            cleaned.update(self.extra)
        return cleaned


class TraceCollector:
    """Collects and ships traces to the LupisLabs backend."""

    def __init__(
        self,
        *,
        endpoint: Optional[str],
        project_id: str,
        api_key: Optional[str],
        enabled: bool = True,
    ) -> None:
        self.endpoint = endpoint or DEFAULT_TRACES_ENDPOINT
        self.project_id = project_id
        self.api_key = api_key
        self.enabled = enabled
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._in_flight: Set[Future[Any]] = set()
        self._lock = threading.Lock()

    def add_trace(self, trace: HttpTrace) -> None:
        logging.debug("[LupisLabs SDK] Queueing trace: %s %s", trace.method, trace.url)
        future = self._executor.submit(self._send_trace, trace)
        with self._lock:
            self._in_flight.add(future)
        future.add_done_callback(self._handle_future_done)

    def _handle_future_done(self, future: Future[Any]) -> None:
        with self._lock:
            self._in_flight.discard(future)

    def _send_trace(self, trace: HttpTrace) -> None:
        if not self.enabled:
            logging.info("[LupisLabs SDK] Trace (not sent, disabled)")
            return

        try:
            headers = {
                "Content-Type": "application/json",
                "x-project-id": self.project_id,
            }
            if self.api_key:
                headers["x-api-key"] = self.api_key

            payload = trace.to_payload()
            logging.debug("[LupisLabs SDK] Sending trace payload: %s", json.dumps(payload))

            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=30,
            )
            if response.ok:
                logging.debug("[LupisLabs SDK] Trace sent successfully")
            else:
                logging.error("[LupisLabs SDK] Failed to send trace: %s", response.text)
        except Exception as exc:
            logging.error("[LupisLabs SDK] Error sending trace: %s", exc)

    def force_flush(self, timeout: Optional[float] = None) -> None:
        deadline = time.time() + timeout if timeout else None
        while True:
            with self._lock:
                pending = list(self._in_flight)
            if not pending:
                return

            for future in pending:
                remaining = None
                if deadline:
                    remaining = max(0, deadline - time.time())
                try:
                    future.result(timeout=remaining)
                except Exception as exc:  # pragma: no cover - best effort logging
                    logging.error("[LupisLabs SDK] Trace send failed during flush: %s", exc)

    def shutdown(self) -> None:
        logging.info("[LupisLabs SDK] Shutting down TraceCollector")
        try:
            self.force_flush()
        finally:
            self._executor.shutdown(wait=True)
