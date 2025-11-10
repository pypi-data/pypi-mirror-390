from __future__ import annotations

import json
from typing import Any, Iterable

from ..core import RetryInfo, ValidationError
from ..validation.json_validator import JSONValidator


class RequestLogFormatter:
    """Assemble colored loguru-friendly messages for request handlers."""

    @staticmethod
    def build(
        *,
        kind: str,
        action: str,
        elapsed: float | None = None,
        url: str | None = None,
        status_code: int | None = None,
        errors: Iterable[ValidationError] | None = None,
        response_obj: Any = None,
        exc_type: str | None = None,
        exc_msg: str | None = None,
        response_headers: dict | None = None,
        request_body: Any = None,
        request_headers: dict | None = None,
        len_text: int = None,
        retry: RetryInfo | None = None,
    ) -> str:
        elapsed_block = RequestLogFormatter._elapsed_block(elapsed)
        action_block = RequestLogFormatter._action_block(action)
        status_block = RequestLogFormatter._status_block(status_code, url)
        suffix = ""

        if kind in {"ok", "error"}:
            suffix += RequestLogFormatter._errors_block(errors, retry)
            suffix += RequestLogFormatter._details_block(
                request_headers=request_headers,
                request_body=request_body,
                response_headers=response_headers,
                response_obj=response_obj,
                kind=kind,
                len_text=len_text,
            )
        elif kind == "fail":
            suffix += RequestLogFormatter._exception_block(exc_type, exc_msg)

        return f"{elapsed_block} {action_block}{status_block}{suffix}"

    @staticmethod
    def _elapsed_block(elapsed: float | None) -> str:
        elapsed_value = (elapsed or 0.0)
        colour = RequestLogFormatter._elapsed_colour(elapsed_value)
        return f"<fg {colour}>{elapsed_value:6.3f}с</fg {colour}>"

    @staticmethod
    def _elapsed_colour(value: float) -> str:
        if value < 1.0:
            return "#4b5263"
        if value < 2.0:
            return "#e5c07b"
        if value < 3.5:
            return "#c678dd"
        return "#e06c75"

    @staticmethod
    def _action_block(action: str, width: int = 13) -> str:
        trimmed = action if len(action) <= width else action[: width - 1] + "…"
        return f"[<fg #d7dae0>{trimmed.ljust(width)}</fg #d7dae0>]"

    @staticmethod
    def _status_block(status_code: int | None, url: str | None) -> str:
        code_text, fg, bg, bold = RequestLogFormatter._status_palette(status_code)
        code_repr = RequestLogFormatter._wrap_code(code_text, fg, bg, bold)
        display_url = RequestLogFormatter._fmt_url(url or "N/A")
        link = RequestLogFormatter._link(display_url, url)
        return f"[{code_repr} -> <fg #61afef>{link}</fg #61afef>]"

    @staticmethod
    def _status_palette(status_code: int | None) -> tuple[str, str, str | None, bool]:
        if status_code is None:
            return ("---", "#abb2bf", "#3e4451", False)
        code = int(status_code)
        text = f"{code:>3}"
        if code == 200:
            return text, "#1e2127", "#98c379", True
        if 200 <= code < 300:
            return text, "#1e2127", "#56b6c2", False
        if code == 404:
            return text, "#1e2127", "#e5c07b", True
        if 300 <= code < 400:
            return text, "#1e2127", "#c678dd", False
        if 400 <= code < 500:
            return text, "#ffffff", "#e06c75", False
        if 500 <= code < 600:
            return text, "#ffffff", "#be5046", False
        return text, "#d7dae0", "#3e4451", False

    @staticmethod
    def _wrap_code(text: str, fg: str, bg: str | None, bold: bool) -> str:
        inner = f" {text} "
        if bold:
            inner = f"<bold>{inner}</bold>"
        result = f"<fg {fg}>{inner}</fg {fg}>" if fg else inner
        if bg:
            result = f"<bg {bg}>{result}</bg {bg}>"
        return result

    @staticmethod
    def _fmt_url(url: str, max_length: int = 48) -> str:
        stripped = url.replace("https://", "").replace("http://", "")
        return stripped if len(stripped) <= max_length else f"{stripped[:max_length-3]}..."

    @staticmethod
    def _link(display: str, raw: str | None) -> str:
        target = raw if raw else display
        if target.startswith("http"):
            return f"\033[4m{target}\033[24m"
        return display

    @staticmethod
    def _errors_block(errors: Iterable[ValidationError] | None, retry: RetryInfo | None) -> str:
        if not errors:
            return ""
        chunks = []
        retry_block = RequestLogFormatter._retry_block(retry)
        for error in errors:
            key = error.key or "UNKNOWN"
            expected = RequestLogFormatter._limit(str(error.expected))
            actual = RequestLogFormatter._limit(str(error.actual))
            chunks.append(
                " "
                + "[<bg #e06c75><fg #ffffff> ERRORS </fg #ffffff></bg #e06c75>"
                f" -> <fg #e06c75>{key}</fg #e06c75>]{retry_block} <dim>→</dim> <fg #98c379>[{actual}]</fg #98c379>"
                f" <dim>≠</dim> <fg #e06c75>{expected}</fg #e06c75>"
            )
        return "".join(chunks)

    @staticmethod
    def _retry_block(retry: RetryInfo | None) -> str:
        if not retry:
            return ""
        current = max(1, retry.current_attempt)
        maximum = max(1, retry.max_attempts)
        if current <= 1 and maximum <= 1:
            return ""
        return (
            " <dim>[попытка </dim>"
            f"<fg #c678dd>{current}</fg #c678dd>"
            "<dim>/</dim>"
            f"<fg #c678dd>{maximum}</fg #c678dd>"
            "<dim>]</dim>"
        )

    @staticmethod
    def _limit(value: str, limit: int | None = 40) -> str:
        if limit is None:
            return value
        return value if len(value) <= limit else value[: limit - 3] + "..."

    @staticmethod
    def _exception_block(exc_type: str | None, exc_msg: str | None) -> str:
        ty = exc_type or "Exception"
        msg = RequestLogFormatter._limit(exc_msg or "", 60)
        return f" [<bg #e06c75><fg #ffffff> FAIL </fg #ffffff></bg #e06c75> -> <fg #e06c75>{ty}</fg #e06c75>:<fg #e5c07b>{msg}</fg #e5c07b>]"

    @staticmethod
    def _details_block(
        *,
        request_headers: dict | None,
        request_body: Any,
        response_headers: dict | None,
        response_obj: Any,
        kind: str,
        len_text: int,
    ) -> str:
        lines: list[str] = []

        request_body_str = RequestLogFormatter._format_request_body(request_body, len_text)
        response_body_str = (
            RequestLogFormatter._extract_response_body(response_obj, len_text)
            if response_obj is not None
            else None
        )

        if request_headers:
            lines.append(f"\n  <dim>└─ request.headers:</dim> <fg #98c379>{request_headers}</fg #98c379>")
        if request_body_str:
            lines.append(f"\n  <dim>└─ request.body:</dim> <fg #98c379>{request_body_str}</fg #98c379>")
        if response_headers:
            lines.append(f"\n  <dim>└─ response.headers:</dim> <fg #5c6370>{response_headers}</fg #5c6370>")
        if response_body_str:
            lines.append(f"\n  <dim>└─ response.body:</dim> <fg #5c6370>{response_body_str}</fg #5c6370>")

        return "".join(lines)

    @staticmethod
    def _format_request_body(body: Any, limit: int | None) -> str | None:
        if not body:
            return None
        if isinstance(body, dict):
            try:
                rendered = json.dumps(body, ensure_ascii=False, indent=2)
            except Exception:
                rendered = str(body)
        else:
            rendered = str(body)
        return RequestLogFormatter._limit(rendered, limit)

    @staticmethod
    def _extract_response_body(response_obj: Any, limit: int | None) -> str | None:
        if not response_obj:
            return None
        data = None
        json_method = getattr(response_obj, "json", None)
        if callable(json_method):
            try:
                data = JSONValidator.normalize(json_method())
            except Exception:
                data = None

        if data is None:
            text_fallback = getattr(response_obj, "text", None)
            if text_fallback:
                data = JSONValidator.normalize(text_fallback)

        if data is not None:
            cleaned = RequestLogFormatter._clean_body_json(data)
            if cleaned:
                rendered = json.dumps(cleaned, ensure_ascii=False, indent=2)
                return RequestLogFormatter._limit(rendered, limit)

        try:
            text = getattr(response_obj, "text", None)
            if text:
                return RequestLogFormatter._limit(text, limit)
        except Exception:
            pass

        try:
            content = getattr(response_obj, "content", None)
            if content:
                decoded = content.decode("utf-8", errors="ignore")
                return RequestLogFormatter._limit(decoded, limit)
        except Exception:
            pass

        return None

    @staticmethod
    def _clean_body_json(data: Any) -> Any:
        if isinstance(data, dict):
            cleaned = {}
            for key, value in data.items():
                if key == "headers":
                    continue
                sub = RequestLogFormatter._clean_body_json(value)
                if sub not in ({}, [], "", None):
                    cleaned[key] = sub
            return cleaned
        if isinstance(data, list):
            cleaned_list = [RequestLogFormatter._clean_body_json(item) for item in data]
            return [item for item in cleaned_list if item not in ({}, [], "", None)]
        return data
