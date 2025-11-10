from __future__ import annotations

import json
import hashlib
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Iterable, Optional, Set
from urllib.parse import urlparse

from ..core.models import WithValid, as_with_valid
from ..validation.json_validator import JSONValidator


class RequestDebugger:
    """Decorator that persists failed responses and unique JSON structures."""

    _saved_structures: Set[str] = set()

    @staticmethod
    def debug(
        *,
        enabled: bool = True,
        save_errors: bool = True,
        save_unique_structures: bool = False,
        debug_dir: str = "debug_request",
    ):
        def decorator(func: Callable[..., Any]):
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                if not enabled:
                    return await func(*args, **kwargs)

                result = await func(*args, **kwargs)

                # ⬇️ всегда приводим к WithValid, но наружу возвращаем исходный result
                validated = RequestDebugger._ensure_with_valid(result)

                resp_obj = getattr(validated, "response", None) or validated
                url = getattr(resp_obj, "url", "unknown")

                if save_errors:
                    RequestDebugger._persist_errors(validated, url, debug_dir)

                if save_unique_structures and not validated.valid.has_errors():
                    RequestDebugger._persist_structure(validated, url, debug_dir)

                # ВОЗВРАЩАЕМ исходный result, не меняя тип!
                return result

            return wrapper

        return decorator

    # --- helpers ---

    @staticmethod
    def _ensure_with_valid(result: Any) -> WithValid[Any]:
        """Гарантируем WithValid[...] даже если вернулся «сырой» response."""
        try:
            return as_with_valid(result)
        except Exception:
            # в крайнем случае «пустая обёртка», чтобы не падать
            class _Dummy:
                response = result
                class _Valid:
                    def has_errors(self): return False
                    ERRORS = []
                valid = _Valid()
            return _Dummy()  # type: ignore[return-value]

    @staticmethod
    def _persist_errors(wv: WithValid[Any], url: str, debug_dir: str) -> None:
        if not hasattr(wv, "valid") or not wv.valid.has_errors():
            return

        errors = [
            {
                "key": e.key,
                "expected": str(e.expected),
                "actual": str(e.actual),
                "message": e.message,
            }
            for e in wv.valid.ERRORS
        ]

        resp = getattr(wv, "response", None)
        payload = {
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "status_code": getattr(resp, "status_code", None),
            "errors": errors,
            "request": RequestDebugger._extract_request_metadata(resp),
            "response": RequestDebugger._extract_response_metadata(resp),
        }

        summary = RequestDebugger._error_summary(errors)
        RequestDebugger._store(debug_dir, url, "errors_json", payload, summary)

    @staticmethod
    def _persist_structure(wv: WithValid[Any], url: str, debug_dir: str) -> None:
        resp = getattr(wv, "response", None) or wv
        json_method = getattr(resp, "json", None)
        data = None

        if callable(json_method):
            try:
                data = JSONValidator.normalize(json_method())
            except Exception:
                data = None

        if data is None:
            fallback = getattr(resp, "text", None)
            if fallback is None:
                fallback = getattr(resp, "content", None)
            data = JSONValidator.normalize(fallback)

        if data is None:
            return

        structure = RequestDebugger._json_structure(data)
        hash_value = RequestDebugger._hash(structure)

        if hash_value in RequestDebugger._saved_structures:
            return

        payload = {
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "status_code": getattr(resp, "status_code", None),
            "structure_hash": hash_value,
            "structure": structure,
            "example_response": data,
        }

        RequestDebugger._store(debug_dir, url, "unique_json", payload)
        RequestDebugger._saved_structures.add(hash_value)

    @staticmethod
    def _extract_request_metadata(response_obj: Any) -> dict:
        request = getattr(response_obj, "request", None)
        return {
            "method": getattr(request, "method", "UNKNOWN") if request else "UNKNOWN",
            "headers": dict(getattr(request, "headers", {}) or {}),
        }

    @staticmethod
    def _extract_response_metadata(response_obj: Any) -> dict:
        headers = dict(getattr(response_obj, "headers", {}) or {})
        # тело берём безопасно
        body: Any = None
        json_method = getattr(response_obj, "json", None)
        if callable(json_method):
            try:
                body = JSONValidator.normalize(json_method())
            except Exception:
                body = None

        if body is None:
            try:
                text = getattr(response_obj, "text", "") or ""
                body = text[:1000]
            except Exception:  # pragma: no cover
                body = "<unavailable>"
        return {"headers": headers, "body": body}

    @staticmethod
    def _store(
        debug_dir: str,
        url: str,
        subfolder: str,
        data: dict,
        summary: Optional[str] = None,
    ) -> Path:
        domain, endpoint = RequestDebugger._sanitize(url)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        directory = Path(debug_dir) / domain / endpoint / subfolder
        directory.mkdir(parents=True, exist_ok=True)

        payload = {"_summary": summary} if summary else {}
        payload.update(data)

        path = directory / f"{timestamp}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    @staticmethod
    def _sanitize(url: str) -> tuple[str, str]:
        parsed = urlparse(url)
        domain = parsed.netloc.split(":")[0] if parsed.netloc else "unknown"
        endpoint = parsed.path.strip("/") or "root"
        safe_endpoint = endpoint.replace("/", "_").replace(":", "_").replace("?", "_")
        return domain, safe_endpoint

    @staticmethod
    def _json_structure(data: Any, path: str = "") -> Any:
        if isinstance(data, dict):
            return {
                "_type": "dict",
                "keys": {
                    key: RequestDebugger._json_structure(value, f"{path}.{key}")
                    for key, value in data.items()
                },
            }
        if isinstance(data, list):
            if not data:
                return {"_type": "list", "items": "empty"}
            return {"_type": "list", "items": RequestDebugger._json_structure(data[0], f"{path}[0]")}
        return type(data).__name__

    @staticmethod
    def _hash(structure: Any) -> str:
        encoded = json.dumps(structure, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(encoded.encode()).hexdigest()

    @staticmethod
    def _error_summary(errors: Iterable[dict]) -> Optional[str]:
        first = next(iter(errors or []), None)
        if not first:
            return None
        key = first.get("key", "UNKNOWN")
        expected = first.get("expected", "")
        actual = first.get("actual", "")
        return f"[{key:<15}] → [{expected}] ≠ [{actual}]"


DebugRecorder = RequestDebugger
