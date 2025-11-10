from __future__ import annotations

import json
import logging
import time
import uuid
from contextvars import ContextVar, Token
from typing import Any, Callable, Dict, Optional, Tuple

import requests

from .cost_utils import calculate_cost
from .providers.provider_detector import detect_provider, resolve_handler
from .sensitive_data_filter import SensitiveDataFilterUtil
from .trace_collector import HttpTrace, TraceCollector
from .types import LupisMetadata, ProviderHandler, ProviderName, SensitiveDataFilter


_INTERCEPTOR_DEPTH: ContextVar[int] = ContextVar("lupis_http_interceptor_depth", default=0)
_BODY_MAX_LENGTH = 1_000_000


class HttpInterceptor:
    """Intercepts HTTP traffic and forwards normalized traces to the TraceCollector."""

    def __init__(
        self,
        trace_collector: TraceCollector,
        project_id: str,
        sensitive_data_filter: Optional[SensitiveDataFilter] = None,
    ) -> None:
        self.trace_collector = trace_collector
        self.project_id = project_id
        self.is_intercepting = False
        self._requests_original_request = requests.Session.request
        self.sensitive_data_filter = SensitiveDataFilterUtil(sensitive_data_filter or SensitiveDataFilter())
        self.current_chat_id: Optional[str] = None
        self.current_metadata: LupisMetadata = {}

        self._http_client_module: Optional[Any] = None
        self._http_client_original_request: Optional[Callable[..., Any]] = None
        self._http_client_original_getresponse: Optional[Callable[..., Any]] = None

        self._urllib3_module: Optional[Any] = None
        self._urllib3_original_urlopen: Optional[Callable[..., Any]] = None

        self._httpx_module: Optional[Any] = None
        self._httpx_original_client_request: Optional[Callable[..., Any]] = None
        self._httpx_original_async_client_request: Optional[Callable[..., Any]] = None

        self._aiohttp_module: Optional[Any] = None
        self._aiohttp_original_request: Optional[Callable[..., Any]] = None

        self._requests_patched = False
        self._http_client_patched = False
        self._urllib3_patched = False
        self._httpx_client_patched = False
        self._httpx_async_client_patched = False
        self._aiohttp_patched = False

    def start_intercepting(self) -> None:
        if self.is_intercepting:
            return
        logging.info(
            "[LupisLabs SDK] Starting HTTP interception (requests, http.client, urllib3, httpx, aiohttp)"
        )
        self.is_intercepting = True
        self._patch_requests()
        self._patch_http_client()
        self._patch_urllib3()
        self._patch_httpx()
        self._patch_aiohttp()

    def stop_intercepting(self) -> None:
        if not self.is_intercepting:
            return
        logging.info("[LupisLabs SDK] Stopping HTTP interception")
        self.is_intercepting = False
        self._unpatch_requests()
        self._unpatch_http_client()
        self._unpatch_urllib3()
        self._unpatch_httpx()
        self._unpatch_aiohttp()

    def set_chat_id(self, chat_id: str) -> None:
        self.current_chat_id = chat_id

    def clear_chat_id(self) -> None:
        self.current_chat_id = None

    def set_metadata(self, metadata: LupisMetadata) -> None:
        if not metadata:
            return
        self.current_metadata.update(metadata)

    def clear_metadata(self) -> None:
        self.current_metadata = {}

    def _enter_interceptor(self) -> Token[int]:
        current_depth = _INTERCEPTOR_DEPTH.get()
        return _INTERCEPTOR_DEPTH.set(current_depth + 1)

    def _exit_interceptor(self, token: Token[int]) -> None:
        _INTERCEPTOR_DEPTH.reset(token)

    def _is_nested_call(self) -> bool:
        return _INTERCEPTOR_DEPTH.get() > 0

    def _should_skip(self, url: Optional[str]) -> bool:
        if not self.is_intercepting:
            return True
        if self._is_nested_call():
            return True
        return self._should_skip_url(url)

    def _should_skip_url(self, url: Optional[str]) -> bool:
        if not url:
            return False
        endpoint = getattr(self.trace_collector, "endpoint", "")
        if endpoint and endpoint in url:
            return True
        if "/api/traces" in url:
            return True
        return False

    def _normalize_headers(self, headers: Any) -> Dict[str, str]:
        normalized: Dict[str, str] = {}
        if not headers:
            return normalized
        try:
            items = headers.items()  # type: ignore[attr-defined]
        except AttributeError:
            try:
                headers_dict = dict(headers)  # type: ignore[arg-type]
            except Exception:  # pylint: disable=broad-except
                return normalized
            items = headers_dict.items()
        for key, value in items:
            normalized[str(key)] = str(value)
        return normalized

    def _headers_to_dict(self, headers: Any) -> Dict[str, str]:
        return self._normalize_headers(headers)

    def _build_url_from_http_client(self, connection: Any, url: str) -> str:
        if url.startswith("http://") or url.startswith("https://"):
            return url
        host = getattr(connection, "host", "") or ""
        if not host:
            return url
        port = getattr(connection, "port", None)
        scheme = getattr(connection, "scheme", None)
        if not scheme:
            default_port = getattr(connection, "default_port", None)
            scheme = "https" if default_port == 443 else "http"
        if port and port not in (80, 443):
            host = f"{host}:{port}"
        if not url.startswith("/"):
            url = f"/{url}"
        return f"{scheme}://{host}{url}"

    def _build_url_from_pool(self, pool: Any, url: str) -> str:
        if url.startswith("http://") or url.startswith("https://") or not hasattr(pool, "host"):
            return url
        scheme = getattr(pool, "scheme", None) or "http"
        host = getattr(pool, "host", "") or ""
        port = getattr(pool, "port", None)
        if port and port not in (80, 443):
            host = f"{host}:{port}"
        if not url.startswith("/"):
            url = f"/{url}"
        return f"{scheme}://{host}{url}"

    def _limit_body_length(self, body: Optional[str]) -> Optional[str]:
        if body is None:
            return None
        if len(body) > _BODY_MAX_LENGTH:
            return f"{body[:_BODY_MAX_LENGTH]}...<truncated>"
        return body

    def _serialize_body_value(self, body: Any) -> Optional[str]:
        if body is None:
            return None
        if isinstance(body, (bytes, bytearray)):
            try:
                return body.decode("utf-8")
            except UnicodeDecodeError:
                return body.decode("utf-8", errors="ignore")
        if isinstance(body, str):
            return body
        if isinstance(body, (dict, list, tuple)):
            try:
                return json.dumps(body)
            except (TypeError, ValueError):
                return str(body)
        return str(body)

    def _sanitize_request_body_text(self, body_text: Optional[str]) -> Optional[str]:
        if body_text is None:
            return None
        try:
            sanitized = self.sensitive_data_filter.filter_request_body(body_text)
        except Exception:  # pragma: no cover - defensive
            sanitized = body_text
        return self._limit_body_length(sanitized)

    def _sanitize_response_body_text(self, body_text: Optional[str]) -> Optional[str]:
        if body_text is None:
            return None
        try:
            sanitized = self.sensitive_data_filter.filter_response_body(body_text)
        except Exception:  # pragma: no cover - defensive
            sanitized = body_text
        return self._limit_body_length(sanitized)

    def _extract_request_body_from_kwargs(self, kwargs: Dict[str, Any]) -> Optional[str]:
        if not kwargs:
            return None
        if "json" in kwargs and kwargs["json"] is not None:
            return self._serialize_body_value(kwargs["json"])
        if "data" in kwargs and kwargs["data"] is not None:
            return self._serialize_body_value(kwargs["data"])
        if "content" in kwargs and kwargs["content"] is not None:
            return self._serialize_body_value(kwargs["content"])
        if "files" in kwargs and kwargs["files"] is not None:
            return "<files omitted>"
        return None

    def _extract_request_body_from_aiohttp_kwargs(self, kwargs: Dict[str, Any]) -> Optional[str]:
        if not kwargs:
            return None
        if "json" in kwargs and kwargs["json"] is not None:
            return self._serialize_body_value(kwargs["json"])
        if "data" in kwargs and kwargs["data"] is not None:
            return self._serialize_body_value(kwargs["data"])
        return None

    def _extract_usage_metadata(
        self,
        *,
        handler: Optional[ProviderHandler],
        provider: ProviderName,
        response_text: Optional[str],
        json_loader: Optional[Callable[[], Any]],
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], Optional[str]]:
        token_usage: Optional[Dict[str, Any]] = None
        cost_breakdown: Optional[Dict[str, Any]] = None
        model: Optional[str] = None

        def _process_streaming_payload(text: str) -> Optional[Dict[str, Any]]:
            if not handler or not text:
                return None

            chunks = text.split("\n\n")
            state: Any = None
            saw_stream_chunk = False
            for chunk in chunks:
                chunk = chunk.strip()
                if not chunk:
                    continue
                if not handler.is_streaming_chunk(chunk):
                    continue
                saw_stream_chunk = True
                try:
                    accumulator = handler.accumulate_chunk(state, chunk)
                except Exception:  # pragma: no cover - defensive
                    continue
                state = accumulator.get("state", state)
            return state if saw_stream_chunk else None

        def _resolve_model(payload: Any) -> Optional[str]:
            if not isinstance(payload, dict):
                return None
            if payload.get("model"):
                return payload["model"]
            message_field = payload.get("message")
            if isinstance(message_field, dict):
                model_value = message_field.get("model")
                if isinstance(model_value, str):
                    return model_value
            return None

        streaming_state: Optional[Dict[str, Any]] = None

        if handler and response_text:
            parsed_successfully = False
            try:
                normalized = handler.normalize_final(response_text)
                parsed_successfully = isinstance(normalized, dict)
            except Exception as normalize_error:  # pylint: disable=broad-except
                logging.debug(
                    "[LupisLabs SDK] Failed to normalize response body: %s", normalize_error
                )
                normalized = None

            if isinstance(normalized, dict):
                usage = normalized.get("usage")
                model_candidate = _resolve_model(normalized)
                if usage:
                    usage_data, cost_data = calculate_cost(usage, provider, model_candidate)
                    if usage_data:
                        token_usage = usage_data
                    if cost_data:
                        cost_breakdown = cost_data
                if model_candidate:
                    model = model_candidate

            if not parsed_successfully:
                streaming_state = _process_streaming_payload(response_text or "")

        if json_loader and (token_usage is None or model is None):
            try:
                raw_json = json_loader()
            except Exception as json_error:  # pylint: disable=broad-except
                logging.debug("[LupisLabs SDK] Failed to parse JSON response: %s", json_error)
            else:
                if isinstance(raw_json, dict):
                    usage = raw_json.get("usage")
                    model_candidate = _resolve_model(raw_json)
                    if usage and token_usage is None:
                        usage_data, cost_data = calculate_cost(usage, provider, model_candidate)
                        if usage_data:
                            token_usage = usage_data
                        if cost_data:
                            cost_breakdown = cost_data
                    if model_candidate and model is None:
                        model = model_candidate

        if streaming_state and not token_usage:
            usage = streaming_state.get("__usage")  # type: ignore[assignment]
            model_candidate = streaming_state.get("model")
            if usage:
                usage_data, cost_data = calculate_cost(usage, provider, model_candidate)
                if usage_data:
                    token_usage = usage_data
                if cost_data:
                    cost_breakdown = cost_data
            if model_candidate and model is None:
                model = model_candidate

        return token_usage, cost_breakdown, model

    def _finalize_http_client_trace(self, connection: Any, context: Dict[str, Any], response: Any) -> None:
        duration_ms = context.get("duration")
        if duration_ms is None:
            start_time = context.get("start_time")
            if isinstance(start_time, (int, float)):
                duration_ms = int((time.perf_counter() - start_time) * 1000)
            else:
                duration_ms = 0

        status_code = getattr(response, "status", 0) if response is not None else 0
        response_headers: Dict[str, str] = {}
        if response is not None:
            try:
                response_headers = {str(key): str(value) for key, value in response.getheaders()}  # type: ignore[attr-defined]
            except Exception:  # pylint: disable=broad-except
                response_headers = {}
        filtered_response_headers = self.sensitive_data_filter.filter_headers(response_headers)

        trace = self._create_trace(
            url=context.get("url", ""),
            method=context.get("method", "GET"),
            status_code=status_code,
            duration=duration_ms,
            provider=context.get("provider", "unknown"),
            request_headers=context.get("request_headers", {}),
            response_headers=filtered_response_headers,
            token_usage=None,
            cost_breakdown=None,
            model=None,
            request_body=context.get("request_body"),
            response_body=context.get("response_body"),
            error=context.get("error"),
        )
        self.trace_collector.add_trace(trace)
        if hasattr(connection, "_lupis_context"):
            try:
                delattr(connection, "_lupis_context")
            except AttributeError:
                pass

    def _patch_requests(self) -> None:
        if self._requests_patched:
            return

        interceptor = self
        original_request = self._requests_original_request

        def patched_request(session: requests.Session, method: str, url: str, **kwargs: Any):  # type: ignore[override]
            if interceptor._should_skip(url):
                return original_request(session, method, url, **kwargs)

            request_headers = interceptor._normalize_headers(kwargs.get("headers"))
            filtered_request_headers = interceptor.sensitive_data_filter.filter_headers(request_headers)

            raw_request_body = interceptor._extract_request_body_from_kwargs(kwargs)
            sanitized_request_body = interceptor._sanitize_request_body_text(raw_request_body)

            provider = detect_provider(url)
            handler = resolve_handler(provider)

            response = None
            error_text = None
            token = interceptor._enter_interceptor()
            start_time = time.perf_counter()

            try:
                response = original_request(session, method, url, **kwargs)
            except Exception as error:  # pylint: disable=broad-except
                logging.exception("[LupisLabs SDK] HTTP request failed: %s", error)
                error_text = str(error)
                raise
            finally:
                duration_ms = int((time.perf_counter() - start_time) * 1000)
                status_code = response.status_code if response is not None else 0
                filtered_response_headers: Dict[str, str] = {}
                token_usage: Optional[Dict[str, Any]] = None
                cost_breakdown: Optional[Dict[str, Any]] = None
                model: Optional[str] = None
                sanitized_response_body: Optional[str] = None

                if response is not None:
                    response_headers = interceptor._headers_to_dict(response.headers)
                    filtered_response_headers = interceptor.sensitive_data_filter.filter_headers(response_headers)

                    response_text: Optional[str] = None
                    try:
                        response_text = response.text
                    except Exception:  # pylint: disable=broad-except
                        response_text = None

                    json_loader: Optional[Callable[[], Any]] = None
                    if hasattr(response, "json"):
                        json_loader = response.json  # type: ignore[assignment]

                    usage_data, cost_data, model_name = interceptor._extract_usage_metadata(
                        handler=handler,
                        provider=provider,
                        response_text=response_text,
                        json_loader=json_loader,
                    )
                    if usage_data:
                        token_usage = usage_data
                    if cost_data:
                        cost_breakdown = cost_data
                    if model_name:
                        model = model_name

                    sanitized_response_body = interceptor._sanitize_response_body_text(response_text)

                trace = interceptor._create_trace(
                    url=url,
                    method=method,
                    status_code=status_code,
                    duration=duration_ms,
                    provider=provider,
                    request_headers=filtered_request_headers,
                    response_headers=filtered_response_headers,
                    token_usage=token_usage,
                    cost_breakdown=cost_breakdown,
                    model=model,
                    request_body=sanitized_request_body,
                    response_body=sanitized_response_body,
                    error=error_text,
                )
                interceptor.trace_collector.add_trace(trace)
                interceptor._exit_interceptor(token)

            return response

        requests.Session.request = patched_request  # type: ignore[assignment]
        self._requests_patched = True

    def _unpatch_requests(self) -> None:
        if not self._requests_patched:
            return
        requests.Session.request = self._requests_original_request
        self._requests_patched = False

    def _patch_http_client(self) -> None:
        if self._http_client_patched:
            return
        try:
            import http.client as http_client  # pylint: disable=import-outside-toplevel
        except ImportError:  # pragma: no cover
            logging.debug("[LupisLabs SDK] http.client not available for interception")
            return

        original_request = http_client.HTTPConnection.request
        original_getresponse = http_client.HTTPConnection.getresponse
        interceptor = self

        def patched_request(connection: Any, method: str, url: str, body: Any = None, headers: Any = None, *args: Any, **kwargs: Any):
            full_url = interceptor._build_url_from_http_client(connection, url)
            if interceptor._should_skip(full_url):
                return original_request(connection, method, url, body=body, headers=headers, *args, **kwargs)

            request_headers = interceptor._normalize_headers(headers)
            filtered_request_headers = interceptor.sensitive_data_filter.filter_headers(request_headers)

            raw_body_text = interceptor._serialize_body_value(body)
            sanitized_request_body = interceptor._sanitize_request_body_text(raw_body_text)

            provider = detect_provider(full_url)
            context = {
                "url": full_url,
                "method": method,
                "provider": provider,
                "start_time": time.perf_counter(),
                "request_headers": filtered_request_headers,
                "request_body": sanitized_request_body,
            }
            setattr(connection, "_lupis_context", context)

            token = interceptor._enter_interceptor()
            try:
                return original_request(connection, method, url, body=body, headers=headers, *args, **kwargs)
            except Exception as error:  # pylint: disable=broad-except
                logging.exception("[LupisLabs SDK] HTTP request failed: %s", error)
                context["error"] = str(error)
                context["duration"] = int((time.perf_counter() - context["start_time"]) * 1000)
                interceptor._finalize_http_client_trace(connection, context, response=None)
                raise
            finally:
                interceptor._exit_interceptor(token)

        def patched_getresponse(connection: Any, *args: Any, **kwargs: Any):
            context = getattr(connection, "_lupis_context", None)
            if not isinstance(context, dict):
                return original_getresponse(connection, *args, **kwargs)

            token = interceptor._enter_interceptor()
            try:
                response = original_getresponse(connection, *args, **kwargs)
            except Exception as error:  # pylint: disable=broad-except
                logging.exception("[LupisLabs SDK] HTTP getresponse failed: %s", error)
                context["error"] = str(error)
                context["duration"] = int((time.perf_counter() - context.get("start_time", time.perf_counter())) * 1000)
                interceptor._exit_interceptor(token)
                interceptor._finalize_http_client_trace(connection, context, response=None)
                raise

            interceptor._exit_interceptor(token)
            context["duration"] = int((time.perf_counter() - context.get("start_time", time.perf_counter())) * 1000)
            interceptor._finalize_http_client_trace(connection, context, response=response)
            return response

        http_client.HTTPConnection.request = patched_request  # type: ignore[assignment]
        http_client.HTTPConnection.getresponse = patched_getresponse  # type: ignore[assignment]
        if hasattr(http_client, "HTTPSConnection"):
            http_client.HTTPSConnection.request = patched_request  # type: ignore[attr-defined,assignment]
            http_client.HTTPSConnection.getresponse = patched_getresponse  # type: ignore[attr-defined,assignment]

        self._http_client_module = http_client
        self._http_client_original_request = original_request
        self._http_client_original_getresponse = original_getresponse
        self._http_client_patched = True

    def _unpatch_http_client(self) -> None:
        if not self._http_client_patched or self._http_client_module is None:
            return
        http_client = self._http_client_module
        if self._http_client_original_request is not None:
            http_client.HTTPConnection.request = self._http_client_original_request  # type: ignore[assignment]
            if hasattr(http_client, "HTTPSConnection"):
                http_client.HTTPSConnection.request = self._http_client_original_request  # type: ignore[attr-defined,assignment]
        if self._http_client_original_getresponse is not None:
            http_client.HTTPConnection.getresponse = self._http_client_original_getresponse  # type: ignore[assignment]
            if hasattr(http_client, "HTTPSConnection"):
                http_client.HTTPSConnection.getresponse = self._http_client_original_getresponse  # type: ignore[attr-defined,assignment]
        self._http_client_patched = False
        self._http_client_module = None

    def _patch_urllib3(self) -> None:
        if self._urllib3_patched:
            return
        try:
            import urllib3  # pylint: disable=import-outside-toplevel
        except ImportError:  # pragma: no cover
            logging.debug("[LupisLabs SDK] urllib3 not available for interception")
            return

        original_urlopen = urllib3.connectionpool.HTTPConnectionPool.urlopen
        interceptor = self

        def patched_urlopen(pool: Any, method: str, url: str, body: Any = None, headers: Any = None, *args: Any, **kwargs: Any):
            full_url = interceptor._build_url_from_pool(pool, url)
            if interceptor._should_skip(full_url):
                return original_urlopen(pool, method, url, body=body, headers=headers, *args, **kwargs)

            request_headers = interceptor._normalize_headers(headers)
            filtered_request_headers = interceptor.sensitive_data_filter.filter_headers(request_headers)

            raw_request_body = interceptor._serialize_body_value(body)
            sanitized_request_body = interceptor._sanitize_request_body_text(raw_request_body)

            provider = detect_provider(full_url)
            handler = resolve_handler(provider)

            response = None
            error_text = None
            token = interceptor._enter_interceptor()
            start_time = time.perf_counter()

            try:
                response = original_urlopen(pool, method, url, body=body, headers=headers, *args, **kwargs)
            except Exception as error:  # pylint: disable=broad-except
                logging.exception("[LupisLabs SDK] HTTP request failed: %s", error)
                error_text = str(error)
                raise
            finally:
                duration_ms = int((time.perf_counter() - start_time) * 1000)
                status_code = getattr(response, "status", 0) if response is not None else 0
                filtered_response_headers: Dict[str, str] = {}
                token_usage: Optional[Dict[str, Any]] = None
                cost_breakdown: Optional[Dict[str, Any]] = None
                model: Optional[str] = None
                sanitized_response_body: Optional[str] = None

                if response is not None:
                    response_headers = interceptor._headers_to_dict(response.headers)
                    filtered_response_headers = interceptor.sensitive_data_filter.filter_headers(response_headers)

                    response_text: Optional[str] = None
                    data = getattr(response, "data", None)
                    if isinstance(data, bytes):
                        try:
                            response_text = data.decode("utf-8")
                        except Exception:  # pylint: disable=broad-except
                            response_text = data.decode("utf-8", errors="ignore")
                    elif isinstance(data, str):
                        response_text = data

                    json_loader: Optional[Callable[[], Any]] = None
                    if response_text:

                        def _load_json() -> Any:
                            return json.loads(response_text or "")

                        json_loader = _load_json

                    usage_data, cost_data, model_name = interceptor._extract_usage_metadata(
                        handler=handler,
                        provider=provider,
                        response_text=response_text,
                        json_loader=json_loader,
                    )
                    if usage_data:
                        token_usage = usage_data
                    if cost_data:
                        cost_breakdown = cost_data
                    if model_name:
                        model = model_name

                    sanitized_response_body = interceptor._sanitize_response_body_text(response_text)

                trace = interceptor._create_trace(
                    url=full_url,
                    method=method,
                    status_code=status_code,
                    duration=duration_ms,
                    provider=provider,
                    request_headers=filtered_request_headers,
                    response_headers=filtered_response_headers,
                    token_usage=token_usage,
                    cost_breakdown=cost_breakdown,
                    model=model,
                    request_body=sanitized_request_body,
                    response_body=sanitized_response_body,
                    error=error_text,
                )
                interceptor.trace_collector.add_trace(trace)
                interceptor._exit_interceptor(token)

            return response

        urllib3.connectionpool.HTTPConnectionPool.urlopen = patched_urlopen  # type: ignore[assignment]
        self._urllib3_module = urllib3
        self._urllib3_original_urlopen = original_urlopen
        self._urllib3_patched = True

    def _unpatch_urllib3(self) -> None:
        if not self._urllib3_patched or self._urllib3_module is None:
            return
        self._urllib3_module.connectionpool.HTTPConnectionPool.urlopen = self._urllib3_original_urlopen  # type: ignore[assignment]
        self._urllib3_patched = False
        self._urllib3_module = None

    def _patch_httpx(self) -> None:
        if self._httpx_client_patched and self._httpx_async_client_patched:
            return
        try:
            import httpx  # pylint: disable=import-outside-toplevel
        except ImportError:  # pragma: no cover
            logging.debug("[LupisLabs SDK] httpx not available for interception")
            return

        interceptor = self
        self._httpx_module = httpx

        if not self._httpx_client_patched and hasattr(httpx, "Client"):
            original_client_request = httpx.Client.request

            def patched_client_request(client: Any, method: str, url: Any, **kwargs: Any):
                url_str = str(url)
                if interceptor._should_skip(url_str):
                    return original_client_request(client, method, url, **kwargs)

                request_headers = interceptor._normalize_headers(kwargs.get("headers"))
                filtered_request_headers = interceptor.sensitive_data_filter.filter_headers(request_headers)

                raw_request_body = interceptor._extract_request_body_from_kwargs(kwargs)
                sanitized_request_body = interceptor._sanitize_request_body_text(raw_request_body)

                provider = detect_provider(url_str)
                handler = resolve_handler(provider)

                response = None
                error_text = None
                token = interceptor._enter_interceptor()
                start_time = time.perf_counter()

                try:
                    response = original_client_request(client, method, url, **kwargs)
                except Exception as error:  # pylint: disable=broad-except
                    logging.exception("[LupisLabs SDK] HTTP request failed: %s", error)
                    error_text = str(error)
                    raise
                finally:
                    duration_ms = int((time.perf_counter() - start_time) * 1000)
                    status_code = response.status_code if response is not None else 0
                    filtered_response_headers: Dict[str, str] = {}
                    token_usage: Optional[Dict[str, Any]] = None
                    cost_breakdown: Optional[Dict[str, Any]] = None
                    model: Optional[str] = None
                    sanitized_response_body: Optional[str] = None

                    if response is not None:
                        response_headers = interceptor._headers_to_dict(response.headers)
                        filtered_response_headers = interceptor.sensitive_data_filter.filter_headers(response_headers)

                        response_text: Optional[str] = None
                        try:
                            response_text = response.text
                        except Exception:  # pylint: disable=broad-except
                            response_text = None

                        json_loader: Optional[Callable[[], Any]] = None
                        if hasattr(response, "json"):
                            json_loader = response.json

                        usage_data, cost_data, model_name = interceptor._extract_usage_metadata(
                            handler=handler,
                            provider=provider,
                            response_text=response_text,
                            json_loader=json_loader,
                        )
                        if usage_data:
                            token_usage = usage_data
                        if cost_data:
                            cost_breakdown = cost_data
                        if model_name:
                            model = model_name

                        sanitized_response_body = interceptor._sanitize_response_body_text(response_text)

                    trace = interceptor._create_trace(
                        url=url_str,
                        method=method,
                        status_code=status_code,
                        duration=duration_ms,
                        provider=provider,
                        request_headers=filtered_request_headers,
                        response_headers=filtered_response_headers,
                        token_usage=token_usage,
                        cost_breakdown=cost_breakdown,
                        model=model,
                        request_body=sanitized_request_body,
                        response_body=sanitized_response_body,
                        error=error_text,
                    )
                    interceptor.trace_collector.add_trace(trace)
                    interceptor._exit_interceptor(token)

                return response

            httpx.Client.request = patched_client_request  # type: ignore[assignment]
            self._httpx_original_client_request = original_client_request
            self._httpx_client_patched = True

        if hasattr(httpx, "AsyncClient") and not self._httpx_async_client_patched:
            original_async_request = httpx.AsyncClient.request

            async def patched_async_request(client: Any, method: str, url: Any, **kwargs: Any):
                url_str = str(url)
                if interceptor._should_skip(url_str):
                    return await original_async_request(client, method, url, **kwargs)

                request_headers = interceptor._normalize_headers(kwargs.get("headers"))
                filtered_request_headers = interceptor.sensitive_data_filter.filter_headers(request_headers)

                raw_request_body = interceptor._extract_request_body_from_kwargs(kwargs)
                sanitized_request_body = interceptor._sanitize_request_body_text(raw_request_body)

                provider = detect_provider(url_str)
                handler = resolve_handler(provider)

                response = None
                error_text = None
                token = interceptor._enter_interceptor()
                start_time = time.perf_counter()

                try:
                    response = await original_async_request(client, method, url, **kwargs)
                except Exception as error:  # pylint: disable=broad-except
                    logging.exception("[LupisLabs SDK] HTTP request failed: %s", error)
                    error_text = str(error)
                    raise
                finally:
                    duration_ms = int((time.perf_counter() - start_time) * 1000)
                    status_code = response.status_code if response is not None else 0
                    filtered_response_headers: Dict[str, str] = {}
                    token_usage: Optional[Dict[str, Any]] = None
                    cost_breakdown: Optional[Dict[str, Any]] = None
                    model: Optional[str] = None
                    sanitized_response_body: Optional[str] = None

                    if response is not None:
                        response_headers = interceptor._headers_to_dict(response.headers)
                        filtered_response_headers = interceptor.sensitive_data_filter.filter_headers(response_headers)

                        response_text: Optional[str] = None
                        try:
                            response_text = response.text
                        except Exception:  # pylint: disable=broad-except
                            response_text = None

                        json_loader: Optional[Callable[[], Any]] = None
                        if hasattr(response, "json"):
                            json_loader = response.json

                        usage_data, cost_data, model_name = interceptor._extract_usage_metadata(
                            handler=handler,
                            provider=provider,
                            response_text=response_text,
                            json_loader=json_loader,
                        )
                        if usage_data:
                            token_usage = usage_data
                        if cost_data:
                            cost_breakdown = cost_data
                        if model_name:
                            model = model_name

                        sanitized_response_body = interceptor._sanitize_response_body_text(response_text)

                    trace = interceptor._create_trace(
                        url=url_str,
                        method=method,
                        status_code=status_code,
                        duration=duration_ms,
                        provider=provider,
                        request_headers=filtered_request_headers,
                        response_headers=filtered_response_headers,
                        token_usage=token_usage,
                        cost_breakdown=cost_breakdown,
                        model=model,
                        request_body=sanitized_request_body,
                        response_body=sanitized_response_body,
                        error=error_text,
                    )
                    interceptor.trace_collector.add_trace(trace)
                    interceptor._exit_interceptor(token)

                return response

            httpx.AsyncClient.request = patched_async_request  # type: ignore[assignment]
            self._httpx_original_async_client_request = original_async_request
            self._httpx_async_client_patched = True

    def _unpatch_httpx(self) -> None:
        if self._httpx_module is None:
            return
        httpx = self._httpx_module
        if self._httpx_client_patched and self._httpx_original_client_request is not None:
            httpx.Client.request = self._httpx_original_client_request  # type: ignore[assignment]
            self._httpx_client_patched = False
        if (
            hasattr(httpx, "AsyncClient")
            and self._httpx_async_client_patched
            and self._httpx_original_async_client_request is not None
        ):
            httpx.AsyncClient.request = self._httpx_original_async_client_request  # type: ignore[assignment]
            self._httpx_async_client_patched = False
        if not self._httpx_client_patched and not self._httpx_async_client_patched:
            self._httpx_module = None

    def _patch_aiohttp(self) -> None:
        if self._aiohttp_patched:
            return
        try:
            import aiohttp  # pylint: disable=import-outside-toplevel
        except ImportError:  # pragma: no cover
            logging.debug("[LupisLabs SDK] aiohttp not available for interception")
            return

        original_request = aiohttp.ClientSession._request
        interceptor = self

        async def patched_request(session: Any, method: str, url: Any, **kwargs: Any):
            url_str = str(url)
            if interceptor._should_skip(url_str):
                return await original_request(session, method, url, **kwargs)

            request_headers = interceptor._normalize_headers(kwargs.get("headers"))
            filtered_request_headers = interceptor.sensitive_data_filter.filter_headers(request_headers)

            raw_request_body = interceptor._extract_request_body_from_aiohttp_kwargs(kwargs)
            sanitized_request_body = interceptor._sanitize_request_body_text(raw_request_body)

            provider = detect_provider(url_str)

            response = None
            error_text = None
            token = interceptor._enter_interceptor()
            start_time = time.perf_counter()

            try:
                response = await original_request(session, method, url, **kwargs)
            except Exception as error:  # pylint: disable=broad-except
                logging.exception("[LupisLabs SDK] HTTP request failed: %s", error)
                error_text = str(error)
                raise
            finally:
                duration_ms = int((time.perf_counter() - start_time) * 1000)
                status_code = response.status if response is not None else 0
                filtered_response_headers: Dict[str, str] = {}
                sanitized_response_body: Optional[str] = None
                if response is not None:
                    response_headers = interceptor._headers_to_dict(response.headers)
                    filtered_response_headers = interceptor.sensitive_data_filter.filter_headers(response_headers)
                    try:
                        response_text = await response.text()
                    except Exception:  # pylint: disable=broad-except
                        response_text = None
                    sanitized_response_body = interceptor._sanitize_response_body_text(response_text)
                    if response_text is None:
                        # Restore stream by buffering? response.text already reads body. Nothing to do.
                        pass

                trace = interceptor._create_trace(
                    url=url_str,
                    method=method,
                    status_code=status_code,
                    duration=duration_ms,
                    provider=provider,
                    request_headers=filtered_request_headers,
                    response_headers=filtered_response_headers,
                    token_usage=None,
                    cost_breakdown=None,
                    model=None,
                    request_body=sanitized_request_body,
                    response_body=sanitized_response_body,
                    error=error_text,
                )
                interceptor.trace_collector.add_trace(trace)
                interceptor._exit_interceptor(token)

            return response

        aiohttp.ClientSession._request = patched_request  # type: ignore[assignment]
        self._aiohttp_module = aiohttp
        self._aiohttp_original_request = original_request
        self._aiohttp_patched = True

    def _unpatch_aiohttp(self) -> None:
        if not self._aiohttp_patched or self._aiohttp_module is None:
            return
        self._aiohttp_module.ClientSession._request = self._aiohttp_original_request  # type: ignore[assignment]
        self._aiohttp_patched = False
        self._aiohttp_module = None

    def _create_trace(
        self,
        *,
        url: str,
        method: str,
        status_code: int,
        duration: int,
        provider: ProviderName,
        request_headers: Dict[str, str],
        response_headers: Dict[str, str],
        token_usage: Optional[Dict[str, Any]],
        cost_breakdown: Optional[Dict[str, Any]],
        model: Optional[str],
        request_body: Optional[str],
        response_body: Optional[str],
        error: Optional[str],
    ) -> HttpTrace:
        trace_id = f"{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        metadata = dict(self.current_metadata) if self.current_metadata else None

        return HttpTrace(
            id=trace_id,
            project_id=self.project_id,
            timestamp=int(time.time() * 1000),
            duration=duration,
            url=url,
            method=method.upper(),
            status_code=status_code,
            provider=provider,
            request_headers=request_headers or None,
            response_headers=response_headers or None,
            token_usage=token_usage,
            cost_breakdown=cost_breakdown,
            model=model,
            request_body=request_body,
            response_body=response_body,
            chat_id=self.current_chat_id,
            metadata=metadata,
            error=error,
        )
