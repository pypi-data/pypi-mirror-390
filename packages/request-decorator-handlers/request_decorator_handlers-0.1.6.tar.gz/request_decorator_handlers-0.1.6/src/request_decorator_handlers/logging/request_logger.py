from __future__ import annotations

import time
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Literal

from loguru import logger

from .formatter import RequestLogFormatter
from ..core.models import RetryContext, WithValid, as_with_valid

LogLevel = Literal["full", "success_error", "error_only"]
_LOG_NAMESPACE = "request_decorator_handlers"

# По умолчанию не шумим, пока пользователь явно не включит.
logger.enable(_LOG_NAMESPACE)


class RequestLogger:
    """Decorator that logs request/response lifecycle with validation support."""

    @staticmethod
    def enable() -> None:
        """Разрешить вывод логов библиотеки."""
        logger.enable(_LOG_NAMESPACE)

    @staticmethod
    def disable() -> None:
        """Полностью отключить вывод логов библиотеки."""
        logger.disable(_LOG_NAMESPACE)

    @staticmethod
    def mute() -> None:
        """Синоним disable() для совместимости."""
        RequestLogger.disable()

    @staticmethod
    def unmute() -> None:
        """Синоним enable() для совместимости."""
        RequestLogger.enable()

    @staticmethod
    def is_enabled() -> bool:
        """Проверить, активирован ли вывод логов."""
        module_name = "request_decorator_handlers.logging.request_logger"
        for pattern, state in reversed(logger._core.activation_list):  # type: ignore[attr-defined]
            prefix = pattern[:-1] if pattern.endswith(".") else pattern
            if module_name.startswith(prefix):
                return state
        return True

    @staticmethod
    @contextmanager
    def muted() -> Any:
        """Контекстный менеджер для временного отключения логов."""
        activation_list = logger._core.activation_list  # type: ignore[attr-defined]
        previous_len = len(activation_list)
        logger.disable(_LOG_NAMESPACE)
        try:
            yield
        finally:
            while len(activation_list) > previous_len:
                activation_list.pop()

    @staticmethod
    def log(
            action: str,
            log_level: LogLevel = "full",
            show_body: bool = False,
            len_text: int = None,
            show_response_headers: bool = False,
            show_request_body: bool = False,
            show_request_headers: bool = False,
            enabled: bool = True,
    ):
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                if not enabled:
                    return await func(*args, **kwargs)

                request_url = RequestLogger._extract_url(args, kwargs)
                req_body = RequestLogger._extract_request_body(kwargs) if show_request_body else None
                req_headers = kwargs.get("headers") if show_request_headers else None

                if log_level == "full":
                    logger.opt(colors=True).debug(
                        RequestLogFormatter.build(
                            kind="start",
                            action=action,
                            url=request_url,
                            request_headers=req_headers,
                            request_body=req_body,
                            len_text=len_text,
                        )
                    )

                started_at = time.time()

                try:
                    result = await func(*args, **kwargs)
                    elapsed = time.time() - started_at

                    is_wrapped = isinstance(result, WithValid)
                    validated = result if is_wrapped else as_with_valid(result)

                    validated.valid.ACTION = action

                    response = validated.response

                    if hasattr(response, "url"):
                        request_url = str(response.url) or request_url

                    has_errors = validated.valid.has_errors()
                    resp_headers = (
                        RequestLogger._to_dict(getattr(response, "headers", None))
                        if show_response_headers
                        else None
                    )

                    if show_request_headers and not req_headers:
                        req_headers = RequestLogger._extract_headers_from_response(response)

                    retry_info = getattr(validated.valid, "RETRY", None)
                    if (
                        not retry_info
                        or (
                            getattr(retry_info, "max_attempts", 1) == 1
                            and getattr(retry_info, "current_attempt", 1) == 1
                        )
                    ):
                        ctx_retry = RetryContext.get()
                        if ctx_retry:
                            retry_info = ctx_retry

                    message = RequestLogFormatter.build(
                        kind="error" if has_errors else "ok",
                        action=action,
                        elapsed=elapsed,
                        status_code=getattr(response, "status_code", None),
                        url=request_url,
                        errors=validated.valid.ERRORS if has_errors else None,
                        response_obj=response if show_body else None,
                        response_headers=resp_headers,
                        request_headers=req_headers,
                        request_body=req_body,
                        len_text=len_text,
                        retry=retry_info,
                    )

                    if has_errors:
                        if log_level in {"full", "success_error", "error_only"}:
                            logger.opt(colors=True).error(message)
                    else:
                        if log_level in {"full", "success_error"}:
                            logger.opt(colors=True).success(message)

                    return result

                except Exception as exc:
                    elapsed = time.time() - started_at

                    if log_level in {"full", "success_error", "error_only"}:
                        logger.opt(colors=True).error(
                            RequestLogFormatter.build(
                                kind="fail",
                                action=action,
                                elapsed=elapsed,
                                url=request_url,
                                exc_type=type(exc).__name__,
                                exc_msg=str(exc),
                                request_body=req_body,
                                request_headers=req_headers,
                                len_text=len_text,
                            )
                        )
                    raise

            return wrapper

        return decorator

    @staticmethod
    def _extract_url(args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
        for value in list(args) + list(kwargs.values()):
            if isinstance(value, str) and value.startswith(("http://", "https://")):
                return value
        return "N/A"

    @staticmethod
    def _extract_request_body(kwargs: dict[str, Any]) -> Any:
        if "json" in kwargs:
            return kwargs["json"]
        if "data" in kwargs:
            return kwargs["data"]
        return None

    @staticmethod
    def _extract_headers_from_response(response: Any) -> dict | None:
        try:
            request = getattr(response, "request", None)
            headers = getattr(request, "headers", None)
            return dict(headers) if headers else None
        except Exception:
            return None

    @staticmethod
    def _to_dict(headers: Any) -> dict | None:
        try:
            return dict(headers) if headers else None
        except Exception:
            return None
