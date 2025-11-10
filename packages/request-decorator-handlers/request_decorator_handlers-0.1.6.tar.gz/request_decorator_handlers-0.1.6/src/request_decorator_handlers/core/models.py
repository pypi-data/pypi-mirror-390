from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from typing import (
    Any, Awaitable, Callable, Dict, Generic, Iterable,
    List, Literal, Optional, ParamSpec, TypeVar, Union
)
# Типовые переменные
P = ParamSpec("P")
T = TypeVar("T")


# ---------- базовые модели ----------

@dataclass
class RetryInfo:
    """Служебная информация о повторных запросах."""

    max_attempts: int = 1
    current_attempt: int = 1

    def update(self, *, current: Optional[int] = None, maximum: Optional[int] = None) -> None:
        """Обновить счётчики попыток."""
        if maximum is not None:
            self.max_attempts = max(1, maximum)
        if current is not None:
            self.current_attempt = max(1, current)


RetryContext: ContextVar[RetryInfo | None] = ContextVar("request_retry_info", default=None)


@dataclass
class ValidationError:
    """Дескриптор одной ошибки валидации."""
    key: str
    expected: Union[List, str, int, Any]
    actual: Union[List, str, int, Any]
    message: Optional[str] = None


    def __str__(self) -> str:
        return self.message or f"Ожидалось {self.expected}, получено {self.actual}"


@dataclass
class ValidationData:
    """Данные валидации, прикрепленные к ответу во время выполнения."""
    ERRORS: List[ValidationError] = field(default_factory=list)
    EVENT: Optional[str] = None
    ACTION: Optional[str] = None
    PARSED: Dict[str, Any] = field(default_factory=dict)
    RETRY: RetryInfo = field(default_factory=RetryInfo)

    def add_error(
            self,
            *,
            key: str,
            expected: Any,
            actual: Any,
            message: Optional[str] = None,
    ) -> None:
        """Добавить ошибку валидации."""
        self.ERRORS.append(
            ValidationError(key=key, expected=expected, actual=actual, message=message)
        )

    def has_errors(self) -> bool:
        """Проверить наличие ошибок валидации."""
        return bool(self.ERRORS)

    def as_dict(self) -> Dict[str, str]:
        """Получить ошибки в виде словаря."""
        return {err.key: str(err) for err in self.ERRORS}

    def set_retry(self, *, current: int, maximum: int) -> None:
        """Обновить информацию о ретраях."""
        self.RETRY.update(current=current, maximum=maximum)


@dataclass
class WithValid(Generic[T]):
    """Обертка над оригинальным ответом с данными валидации."""
    response: T
    valid: ValidationData = field(default_factory=ValidationData)

    def __repr__(self) -> str:
        extras: list[str] = []
        if hasattr(self.response, "status_code"):
            extras.append(f"status={self.response.status_code}")
        if self.valid.has_errors():
            extras.append(f"errors={list(self.valid.as_dict().keys())}")
        if self.valid.EVENT:
            extras.append(f"event={self.valid.EVENT}")
        if self.valid.ACTION:
            extras.append(f"action={self.valid.ACTION}")
        return f"WithValid({' '.join(extras)})"


def as_with_valid(result: Any) -> WithValid:
    """Преобразовать произвольный ответ в WithValid."""
    return result if isinstance(result, WithValid) else WithValid(response=result)
