from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Iterable, List, Literal, ParamSpec, TypeVar, Awaitable
from dataclasses import dataclass, field
from typing import (
    Any, Awaitable, Callable, Dict, Generic, Iterable,
    List, Literal, Optional, ParamSpec, TypeVar, Union
)
import json
import re
import asyncio
from ..core.models import (
    P,
    T,
    RetryContext,
    RetryInfo,
    ValidationData,
    ValidationError,
    WithValid,
    as_with_valid,
)
from .json_validator import JSONValidator

# ========== ОБЩИЕ ФИЛЬТРЫ ==========

class _CommonFilters:
    """Универсальные фильтры для любых данных."""

    @staticmethod
    def filter_by_regex(values: list[Any], pattern: str, flags: int = 0) -> list[str]:
        """Отфильтровать значения по regex."""
        compiled = re.compile(pattern, flags)
        results = []

        for val in values:
            text = str(val) if val is not None else ""
            match = compiled.search(text)
            if match:
                results.append(match.group(1) if match.groups() else match.group(0))

        return results

    @staticmethod
    def filter_by_words(values: list[Any], words: Iterable[str]) -> list[Any]:
        """Отфильтровать значения по наличию хотя бы одного слова."""
        words_list = [w.lower() for w in words]
        results = []

        for val in values:
            text = str(val).lower() if val is not None else ""
            if any(word in text for word in words_list):
                results.append(val)

        return results

    @staticmethod
    def check_value(
            values: list[Any],
            *,
            value: Any = ...,
            is_type: type | None = None,
            range_value: tuple[int | float, int | float] | None = None,
    ) -> list[Any]:
        """Проверить значения по критериям."""
        results = []

        for val in values:
            if value is not ...:
                if val != value:
                    continue

            if is_type is not None:
                if not isinstance(val, is_type):
                    continue

            if range_value is not None:
                try:
                    num_val = float(val) if val is not None else None
                    if num_val is None:
                        continue
                    min_val, max_val = range_value
                    if num_val < min_val or num_val > max_val:
                        continue
                except (ValueError, TypeError):
                    continue

            results.append(val)

        return results

    @staticmethod
    def process_filters(
            values: list[Any],
            *,
            value: Any = ...,
            is_type: type | None = None,
            range_value: tuple[int | float, int | float] | None = None,
            regex: str | None = None,
            regex_flags: int = 0,
            words: Iterable[str] | None = None,
    ) -> list[Any]:
        """Применить все фильтры к значениям."""
        if not values:
            return []

        if any([value is not ..., is_type, range_value is not None]):
            values = _CommonFilters.check_value(
                values,
                value=value,
                is_type=is_type,
                range_value=range_value,
            )

        if regex and values:
            values = _CommonFilters.filter_by_regex(values, regex, regex_flags)

        if words and values:
            values = _CommonFilters.filter_by_words(values, words)

        return values


# ========== JSON HELPERS ==========

class _JSONHelpers:
    """Внутренние хелперы для работы с JSON."""

    @staticmethod
    def normalize_json(data: Any) -> Any:
        """Нормализовать JSON-данные для обработки."""
        if hasattr(data, "json") and callable(data.json):
            try:
                data = data.json()
            except Exception:
                return None

        if isinstance(data, (dict, list, str, bytes)):
            return JSONValidator.normalize(data)

        text = getattr(data, "text", None)
        if text is not None:
            return JSONValidator.normalize(text)

        content = getattr(data, "content", None)
        if content is not None:
            return JSONValidator.normalize(content)

        return JSONValidator.normalize(data)

    @staticmethod
    def extract_by_path(data: Any, path: str) -> list[Any]:
        """Извлечь значения по JSONPath."""
        try:
            from jsonpath_ng import parse
            jsonpath_expr = parse(path)
            matches = jsonpath_expr.find(data)
            return [match.value for match in matches]
        except ImportError:
            raise ImportError(
                "JSONPath parser requires 'jsonpath-ng' library. "
                "Install it with: pip install jsonpath-ng"
            )
        except Exception:
            return []


# ========== HTML HELPERS ==========

class _HTMLHelpers:
    """Внутренние хелперы для работы с HTML."""

    @staticmethod
    def normalize_html(data: Any) -> Any:
        """Нормализовать HTML-данные для обработки."""
        try:
            from lxml import html, etree

            # Если это HTTP response с .text
            if hasattr(data, 'text'):
                text_data = data.text
                if text_data:
                    text_data = text_data.strip()
                    try:
                        return html.document_fromstring(text_data)
                    except Exception:
                        try:
                            return html.fragment_fromstring(text_data, create_parent='div')
                        except Exception:
                            return None

            # Если это строка
            if isinstance(data, str):
                try:
                    data = data.strip()
                    return html.document_fromstring(data)
                except Exception:
                    try:
                        return html.fragment_fromstring(data, create_parent='div')
                    except Exception:
                        return None

            # Уже элемент
            if isinstance(data, (html.HtmlElement, etree._Element)):
                return data

            return None
        except ImportError:
            raise ImportError(
                "HTML parser requires 'lxml' library. "
                "Install it with: pip install lxml"
            )

    @staticmethod
    def extract_by_selector(
            tree: Any,
            selector: str,
            selector_type: Literal["xpath", "css"] = "css",
            extract: Literal["text", "html", "attr"] = "text",
            attr_name: str | None = None,
    ) -> list[str]:
        """Извлечь значения по XPath или CSS селектору."""
        try:
            from lxml import html, etree
            from lxml.cssselect import CSSSelector

            if selector_type == "xpath":
                elements = tree.xpath(selector)
            elif selector_type == "css":
                try:
                    css = CSSSelector(selector)
                    elements = css(tree)
                except Exception:
                    return []
            else:
                return []

            if elements and not isinstance(elements[0], (html.HtmlElement, etree._Element)):
                return [str(e) for e in elements]

            results = []
            for elem in elements:
                if extract == "text":
                    text = elem.text_content().strip()
                    if text:
                        results.append(text)
                elif extract == "html":
                    html_str = etree.tostring(elem, encoding='unicode', method='html')
                    results.append(html_str)
                elif extract == "attr":
                    if attr_name:
                        attr_value = elem.get(attr_name)
                        if attr_value is not None:
                            results.append(attr_value)

            return results
        except Exception:
            return []


# ---------- PARSER AS HANDLER ----------

class Parser:
    """Превращает парсеры в валидаторы-хендлеры для использования в декораторах."""

    @staticmethod
    def HEADER(
        header_key: str,
        save_to: str,
        *,
        regex: str | None = None,
        regex_flags: int = 0,
        words: Iterable[str] | None = None,
        default: Any = None,
    ) -> ValidatorFn:
        """
        Создаёт хендлер для парсинга заголовка.

        Args:
            header_key: Название заголовка
            save_to: Ключ для сохранения в valid.PARSED (обязательно)
            regex: Регулярное выражение для извлечения части значения
            regex_flags: Флаги для regex
            words: Список слов для фильтрации
            default: Значение по умолчанию

        Example:
            @ResponseHandler.handlers(
                Validator.STATUS_CODE([200]),
                ParserHandler.HEADER("Content-Type", save_to="content_type"),
                ParserHandler.HEADER("Server", save_to="server"),
            )
        """
        def handler(response: Any, valid: ValidationData) -> None:
            result = ParserUtil.HEADER(
                response,
                header_key,
                regex=regex,
                regex_flags=regex_flags,
                words=words,
                default=default,
            )
            valid.PARSED[save_to] = result

        return handler

    @staticmethod
    def JSON(
        path: str,
        save_to: str,
        *,
        regex: str | None = None,
        regex_flags: int = 0,
        words: Iterable[str] | None = None,
        return_first: bool = True,
        value: Any = ...,
        is_type: type | None = None,
        range_value: tuple[int | float, int | float] | None = None,
    ) -> ValidatorFn:
        """
        Создаёт хендлер для парсинга JSON.

        Args:
            path: JSONPath выражение
            save_to: Ключ для сохранения в valid.PARSED (обязательно)
            regex: Регулярное выражение для фильтрации
            regex_flags: Флаги для regex
            words: Список слов для фильтрации
            return_first: Вернуть первый результат или список
            value: Фильтр по значению
            is_type: Фильтр по типу
            range_value: Фильтр по диапазону

        Example:
            @ResponseHandler.handlers(
                ParserHandler.JSON("$.user.id", save_to="user_id"),
                ParserHandler.JSON("$.items[*].name", save_to="item_names", return_first=False),
            )
        """
        def handler(response: Any, valid: ValidationData) -> None:
            result = ParserUtil.JSON(
                response,
                path,
                regex=regex,
                regex_flags=regex_flags,
                words=words,
                return_first=return_first,
                value=value,
                is_type=is_type,
                range_value=range_value,
            )
            valid.PARSED[save_to] = result

        return handler

    @staticmethod
    def HTML(
        selector: str,
        save_to: str,
        *,
        selector_type: Literal["xpath", "css"] = "css",
        extract: Literal["text", "html", "attr"] = "text",
        attr_name: str | None = None,
        words: Iterable[str] | None = None,
        return_first: bool = True,
        value: Any = ...,
        is_type: type | None = None,
        range_value: tuple[int | float, int | float] | None = None,
    ) -> ValidatorFn:
        """
        Создаёт хендлер для парсинга HTML.

        Args:
            selector: XPath или CSS селектор
            save_to: Ключ для сохранения в valid.PARSED (обязательно)
            selector_type: "xpath" или "css"
            extract: "text", "html" или "attr"
            attr_name: Имя атрибута для извлечения
            words: Список слов для фильтрации
            return_first: Вернуть первый результат или список
            value: Фильтр по значению
            is_type: Фильтр по типу
            range_value: Фильтр по диапазону

        Example:
            @ResponseHandler.handlers(
                ParserHandler.HTML("div.title", save_to="title"),
                ParserHandler.HTML("//a/@href", save_to="links", selector_type="xpath", return_first=False),
            )
        """
        def handler(response: Any, valid: ValidationData) -> None:
            result = ParserUtil.HTML(
                response,
                selector,
                selector_type=selector_type,
                extract=extract,
                attr_name=attr_name,
                words=words,
                return_first=return_first,
                value=value,
                is_type=is_type,
                range_value=range_value,
            )
            valid.PARSED[save_to] = result

        return handler


# ---------- PARSER ----------

class ParserUtil:
    """Парсеры для извлечения данных из response."""

    @staticmethod
    def HEADER(
        response: Any,
        header_key: str,

        save_to: str | None = None,
        regex: str | None = None,
        regex_flags: int = 0,
        words: Iterable[str] | None = None,
        default: Any = None,
    ) -> dict[str, Any] | Any:
        """
        Извлечь значение заголовка из response.

        Args:
            response: HTTP response объект
            header_key: Название заголовка
            save_to: Ключ для сохранения в valid.PARSED
            regex: Регулярное выражение для извлечения части значения
            regex_flags: Флаги для regex
            words: Список слов для фильтрации
            default: Значение по умолчанию, если заголовок не найден

        Examples:
            Parser.HEADER(response, "Content-Type", save_to="content_type")
            Parser.HEADER(response, "Set-Cookie", regex=r"session=([^;]+)", save_to="session")
        """
        headers = Validator._get_headers(response)
        headers_lower = {k.lower(): v for k, v in headers.items()}
        value = headers_lower.get(header_key.lower())

        if value is None:
            result = default
        else:
            # Применяем regex если указан
            if regex:
                compiled = re.compile(regex, regex_flags)
                match = compiled.search(str(value))
                if match:
                    result = match.group(1) if match.groups() else match.group(0)
                else:
                    result = default
            else:
                result = value

            # Применяем фильтр по словам
            if result is not None and result != default and words:
                words_list = [w.lower() for w in words]
                value_lower = str(result).lower()
                if not any(word in value_lower for word in words_list):
                    result = default

        if save_to:
            return {save_to: result}
        return result

    @staticmethod
    def JSON(
            response: Any,
            path: str,
            *,
            save_to: str | None = None,
            regex: str | None = None,
            regex_flags: int = 0,
            words: Iterable[str] | None = None,
            return_first: bool = True,
            value: Any = ...,
            is_type: type | None = None,
            range_value: tuple[int | float, int | float] | None = None,
    ) -> dict[str, Any] | Any:
        """
        Спарсить JSON из response по JSONPath.

        Args:
            response: HTTP response объект (использует response.json())
            path: JSONPath выражение
            save_to: Ключ для сохранения в valid.PARSED

        Example:
            Parser.JSON(response, "$.user.id", save_to="user_id")
        """
        json_data = _JSONHelpers.normalize_json(response)
        if json_data is None:
            result = None
        else:
            values = _JSONHelpers.extract_by_path(json_data, path)
            values = _CommonFilters.process_filters(
                values,
                value=value,
                is_type=is_type,
                range_value=range_value,
                regex=regex,
                regex_flags=regex_flags,
                words=words,
            )

            if not values:
                result = None
            elif return_first:
                result = values[0]
            else:
                result = values

        if save_to:
            return {save_to: result}
        return result

    @staticmethod
    def HTML(
            response: Any,
            selector: str,
            *,
            save_to: str | None = None,
            selector_type: Literal["xpath", "css"] = "css",
            extract: Literal["text", "html", "attr"] = "text",
            attr_name: str | None = None,
            words: Iterable[str] | None = None,
            return_first: bool = True,
            value: Any = ...,
            is_type: type | None = None,
            range_value: tuple[int | float, int | float] | None = None,
    ) -> dict[str, Any] | Any:
        """
        Спарсить HTML из response по XPath или CSS селектору.

        Args:
            response: HTTP response объект (использует response.text)
            selector: XPath или CSS селектор
            save_to: Ключ для сохранения в valid.PARSED

        Example:
            Parser.HTML(response, "div.username", save_to="username")
        """
        html_tree = _HTMLHelpers.normalize_html(response)
        if html_tree is None:
            result = None
        else:
            values = _HTMLHelpers.extract_by_selector(
                html_tree,
                selector,
                selector_type=selector_type,
                extract=extract,
                attr_name=attr_name,
            )

            values = _CommonFilters.process_filters(
                values,
                value=value,
                is_type=is_type,
                range_value=range_value,
                regex=None,
                regex_flags=0,
                words=words,
            )

            if not values:
                result = None
            elif return_first:
                result = values[0]
            else:
                result = values

        if save_to:
            return {save_to: result}
        return result


# ---------- тип валидатора ----------
ValidatorFn = Callable[[Any, ValidationData], None]


# ---------- класс с валидаторами HTTP ----------
class Validator:
    """Фабрика валидаторов для проверки HTTP-ответов."""

    # ========== HELPERS ==========


    # ========== HTTP VALIDATORS ==========

    @staticmethod
    def STATUS_CODE(allowed: Iterable[int], error_key: str = "STATUS_CODE") -> ValidatorFn:
        """Валидатор статус-кода ответа."""
        allowed_set = set(allowed)

        def validate(response: Any, valid: ValidationData) -> None:
            status_code = Validator._get_attr(response, "status_code", "status", "code")

            if status_code is None:
                valid.add_error(
                    key=error_key,
                    expected=sorted(allowed_set),
                    actual="missing",
                )
            elif status_code not in allowed_set:
                valid.add_error(
                    key=error_key,
                    expected=sorted(allowed_set),
                    actual=status_code,
                )

        return validate

    @staticmethod
    def HEADERS(
        header_key: str,
        expected_value: Any = ...,
        *,
        error_key: str | None = None,
        regex: str | None = None,
        regex_flags: int = 0,
        words: Iterable[str] | None = None,
        exists: bool = True,
    ) -> ValidatorFn:
        """
        Универсальный валидатор заголовка с фильтрами.

        Args:
            header_key: Название заголовка
            expected_value: Ожидаемое значение (точное совпадение)
            error_key: Ключ ошибки (по умолчанию "HEADER_{NAME}")
            regex: Регулярное выражение для проверки
            regex_flags: Флаги для regex
            words: Список слов для проверки наличия
            exists: Проверка наличия (True) или отсутствия (False)

        Examples:
            Validator.headers("Content-Type")  # только проверка наличия
            Validator.headers("Content-Type", expected_value="application/json")  # точное значение
            Validator.headers("User-Agent", regex=r"Mozilla/.*")  # regex проверка
            Validator.headers("Content-Type", words=["json", "application"])  # наличие слов
            Validator.headers("X-Custom", exists=False)  # проверка отсутствия
        """
        if error_key is None:
            error_key = f"HEADER_{header_key.upper().replace('-', '_')}"

        def validate(response: Any, valid: ValidationData) -> None:
            headers = Validator._get_headers(response)
            headers_lower = {k.lower(): v for k, v in headers.items()}
            actual_value = headers_lower.get(header_key.lower())

            if not exists:
                if actual_value is not None:
                    valid.add_error(
                        key=error_key,
                        expected=f"{header_key} not exists",
                        actual=f"{header_key}: {actual_value}",
                    )
                return

            if actual_value is None:
                valid.add_error(
                    key=error_key,
                    expected=f"{header_key} exists",
                    actual="missing",
                )
                return

            # Проверка точного значения
            if expected_value is not ...:
                if actual_value != expected_value:
                    valid.add_error(
                        key=error_key,
                        expected=expected_value,
                        actual=actual_value,
                    )
                    return

            # Проверка через regex
            if regex:
                compiled = re.compile(regex, regex_flags)
                if not compiled.search(str(actual_value)):
                    valid.add_error(
                        key=error_key,
                        expected=f"matches pattern: {regex}",
                        actual=actual_value,
                    )
                    return

            # Проверка через words
            if words:
                words_list = [w.lower() for w in words]
                value_lower = str(actual_value).lower()
                if not any(word in value_lower for word in words_list):
                    valid.add_error(
                        key=error_key,
                        expected=f"contains one of: {list(words)}",
                        actual=actual_value,
                    )

        return validate

    @staticmethod
    def CONTENT_TYPE(
            expected: Literal["json", "html", "image", "text", "bytes"],
            error_key: str = "CONTENT_TYPE",
    ) -> ValidatorFn:
        """Валидатор типа контента."""

        def validate(response: Any, valid: ValidationData) -> None:
            headers = Validator._get_headers(response)
            content_type = (headers.get("content-type", "") or "").lower()

            type_match = {
                "json": "application/json" in content_type,
                "html": "text/html" in content_type,
                "image": "image/" in content_type,
                "text": "text/" in content_type,
                "bytes": True,
            }

            if not type_match.get(expected, False):
                actual = content_type.split(";")[0].strip() if content_type else "unknown"
                valid.add_error(
                    key=error_key,
                    expected=expected,
                    actual=actual,
                )

        return validate

    @staticmethod
    def CLOUFDLARE(
            error_key: str = "CLOUDFLARE",
            keywords: Iterable[str] | None = None,
    ) -> ValidatorFn:
        """Валидатор-детектор Cloudflare защитных страниц."""
        default_keywords = tuple(
            k.lower() for k in (
                "attention required",
                "just a moment",
                "checking your browser",
                "ddos protection",
                "ray id",
                "verify you are human",
                "enable cookies",
                "performance & security",
            )
        )

        def validate(response: Any, valid: ValidationData) -> None:
            text = Validator._get_text(response, "text")
            if not text:
                text = Validator._get_text(response, "content")

            if not text:
                return

            text_lower = text.lower()
            if "cloudflare" not in text_lower:
                return

            indicators = tuple(k.lower() for k in keywords) if keywords else default_keywords
            has_indicator = any(ind in text_lower for ind in indicators)

            if not has_indicator:
                headers = Validator._get_headers(response)
                server_header = (headers.get("server", "") or "").lower()
                has_indicator = (
                    "cloudflare" in server_header
                    or any(key.lower().startswith("cf-") for key in headers)
                )

            if has_indicator:
                valid.add_error(
                    key=error_key,
                    expected="no cloudflare block",
                    actual="cloudflare protection detected",
                )

        return validate

    @staticmethod
    def REGEX(
            pattern: str,
            target: Literal["text", "json", "content"] = "text",
            save_to: str | None = None,
            error_key: str = "REGEX",
            flags: int = 0,
            expect_match: bool = True,
            group: int | None = None,
    ) -> ValidatorFn:
        """Валидатор с использованием регулярного выражения."""
        compiled = re.compile(pattern, flags)

        def validate(response: Any, valid: ValidationData) -> None:
            text = Validator._get_text(response, target)

            if text is None:
                valid.add_error(
                    key=error_key,
                    expected=f"{target} available",
                    actual="unavailable",
                )
                if save_to:
                    valid.PARSED[save_to] = None
                return

            matches = list(compiled.finditer(text))

            if expect_match and not matches:
                valid.add_error(
                    key=error_key,
                    expected=f"pattern matched: {pattern}",
                    actual="not matched",
                )
            elif not expect_match and matches:
                valid.add_error(
                    key=error_key,
                    expected="no matches",
                    actual=f"found {len(matches)} matches",
                )

            if save_to:
                if matches:
                    values = [Validator._extract_regex_group(m, group) for m in matches]
                    valid.PARSED[save_to] = values[0] if len(values) == 1 else values
                else:
                    valid.PARSED[save_to] = None

        return validate

    # ========== JSON/HTML VALIDATORS ==========

    @staticmethod
    def JSON(
            path: str,
            value: Any = ...,
            exists: bool = True,
            words: Iterable[str] | None = None,
            error_key: str = "JSON",
            regex: str | None = None,
            regex_flags: int = 0,
            range_value: tuple[int | float, int | float] | None = None,
            is_type: type | None = None

    ) -> ValidatorFn:
        """
        Валидатор JSON данных из response.

        Args:
            path: JSONPath выражение
            exists: Проверка наличия/отсутствия
            error_key: Ключ ошибки

        Example:
            Validator.JSON("$.user.active", value=True, error_key="USER_ACTIVE")
        """

        def validate(response: Any, valid: ValidationData) -> None:
            json_data = _JSONHelpers.normalize_json(response)

            if json_data is None:
                if exists:
                    valid.add_error(
                        key=error_key,
                        expected="valid JSON",
                        actual="invalid or missing",
                    )
                return

            values = _JSONHelpers.extract_by_path(json_data, path)

            if not exists:
                if len(values) > 0:
                    valid.add_error(
                        key=error_key,
                        expected="field not exists",
                        actual="field exists",
                    )
                return

            if not values:
                valid.add_error(
                    key=error_key,
                    expected=f"field at {path}",
                    actual="not found",
                )
                return

            filtered_values = _CommonFilters.process_filters(
                values,
                value=value,
                is_type=is_type,
                range_value=range_value,
                regex=regex,
                regex_flags=regex_flags,
                words=words,
            )

            if not filtered_values:
                valid.add_error(
                    key=error_key,
                    expected="matching value",
                    actual="no matches after filters",
                )

        return validate

    @staticmethod
    def HTML(
            selector: str,
            selector_type: Literal["xpath", "css"] = "xpath",
            extract: Literal["text", "html", "attr"] = "text",
            exists: bool = True,
            error_key: str = "HTML",
            attr_name: str | None = None,
            words: Iterable[str] | None = None,
            value: Any = ...,
            is_type: type | None = None,
            range_value: tuple[int | float, int | float] | None = None,
    ) -> ValidatorFn:
        """
        Валидатор HTML данных из response.

        Args:
            selector: XPath или CSS селектор
            exists: Проверка наличия/отсутствия
            selector_type: "xpath" или "css"
            error_key: Ключ ошибки

        Example:
            Validator.HTML("div.error", exists=False, error_key="NO_ERRORS")
        """

        def validate(response: Any, valid: ValidationData) -> None:
            html_tree = _HTMLHelpers.normalize_html(response)

            if html_tree is None:
                if exists:
                    valid.add_error(
                        key=error_key,
                        expected="valid HTML",
                        actual="invalid or missing",
                    )
                return

            values = _HTMLHelpers.extract_by_selector(
                html_tree,
                selector,
                selector_type=selector_type,
                extract=extract,
                attr_name=attr_name,
            )

            if not exists:
                if len(values) > 0:
                    valid.add_error(
                        key=error_key,
                        expected="element not exists",
                        actual="element exists",
                    )
                return

            if not values:
                valid.add_error(
                    key=error_key,
                    expected=f"element at {selector}",
                    actual="not found",
                )
                return

            filtered_values = _CommonFilters.process_filters(
                values,
                value=value,
                is_type=is_type,
                range_value=range_value,
                regex=None,
                regex_flags=0,
                words=words,
            )

            if not filtered_values:
                valid.add_error(
                    key=error_key,
                    expected="matching value",
                    actual="no matches after filters",
                )

        return validate

    @staticmethod
    def _get_attr(obj: Any, *attrs: str, default: Any = None) -> Any:
        """Получить первый найденный атрибут из списка вариантов."""
        for attr in attrs:
            value = getattr(obj, attr, None)
            if value is not None:
                return value
        return default

    @staticmethod
    def _get_headers(obj: Any) -> dict[str, Any]:
        """Безопасно извлечь headers как словарь."""
        headers = Validator._get_attr(obj, "headers")
        if isinstance(headers, dict):
            return headers
        try:
            return dict(headers or {})
        except Exception:
            return {}

    @staticmethod
    def _get_text(response: Any, target: Literal["text", "json", "content"]) -> str | None:
        """Извлечь текстовые данные из ответа."""
        if target == "text":
            return Validator._get_attr(response, "text")

        if target == "content":
            content = Validator._get_attr(response, "content")
            if content:
                try:
                    return content.decode("utf-8", errors="ignore")
                except Exception:
                    return None
            return None

        if target == "json":
            json_data: Any = None

            json_method = Validator._get_attr(response, "json")
            if callable(json_method):
                try:
                    json_data = json_method()
                except Exception:
                    json_data = None

            if json_data is None:
                text_data = Validator._get_attr(response, "text")
                if text_data is None:
                    content = Validator._get_attr(response, "content")
                    if isinstance(content, bytes):
                        try:
                            text_data = content.decode("utf-8")
                        except UnicodeDecodeError:
                            text_data = content.decode("utf-8", errors="ignore")
                    else:
                        text_data = content
                json_data = text_data

            normalized = JSONValidator.normalize(json_data)
            if normalized is None:
                return None

            try:
                return json.dumps(normalized, ensure_ascii=False)
            except (TypeError, ValueError):
                return None

        return None

    @staticmethod
    def _get_domain_cookies(session: Any, domain: str) -> dict[str, str]:
        """Извлечь cookies для указанного домена из session."""
        from urllib.parse import urlparse

        parsed = urlparse(domain)
        host = parsed.netloc or parsed.path or domain

        jar = Validator._get_attr(session, "cookies")
        if not jar:
            return {}

        result: dict[str, str] = {}
        try:
            for cookie in jar.jar:
                cookie_domain = getattr(cookie, "domain", "") or ""
                name = getattr(cookie, "name", None)
                value = getattr(cookie, "value", None)

                if name is None or value is None:
                    continue

                if host.endswith(cookie_domain.lstrip(".")):
                    result[name] = value
        except Exception:
            return {}

        return result

    @staticmethod
    def _extract_regex_group(match, group: int | None) -> str:
        """Извлечь группу из regex match с fallback."""
        try:
            if group is None:
                return match.group(1) if match.groups() else match.group(0)
            return match.group(group)
        except IndexError:
            return match.group(0)


# ---------- универсальный декоратор ----------
class ResponseHandler:
    """Декоратор для применения множества валидаторов."""

    @staticmethod
    def handlers(*validators: ValidatorFn) -> Callable[
        [Callable[P, Awaitable[T]]], Callable[P, Awaitable[WithValid[T]]]]:
        """Декоратор для async-функций."""

        def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[WithValid[T]]]:
            @wraps(func)
            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> WithValid[T]:
                response = await func(*args, **kwargs)
                valid = ValidationData()

                # Применяем все валидаторы
                for validator in validators:
                    try:
                        validator(response, valid)
                    except Exception as e:
                        valid.add_error(
                            key="validator_exception",
                            expected="no exception",
                            actual=repr(e),
                            message=str(e),
                        )

                return WithValid(response=response, valid=valid)

            return wrapper

        return decorator

    @staticmethod
    def retry(
            error_key: str | Iterable[str],
            quantity: int = 3,
            interval: float = 0.5,
            enabled: bool = True,
    ):
        """
        Повторяет вызов функции, если после валидации среди ошибок есть указанный error_key.

        :param error_key: ключ или список ключей ошибок валидатора (напр. "CONTENT_TYPE" или ["STATUS_CODE","API_STATUS"])
        :param quantity: максимальное число попыток (включая первую)
        :param interval: задержка между попытками (в секундах)
        :param enabled: глобальный выключатель
        """
        keys = {error_key} if isinstance(error_key, str) else set(error_key)
        keys = {k.upper() for k in keys}  # нормализуем регистр
        if quantity < 1:
            quantity = 1

        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                if not enabled:
                    return await func(*args, **kwargs)

                attempt = 0
                last_result = None

                while True:
                    attempt += 1
                    retry_info = RetryInfo(max_attempts=quantity, current_attempt=attempt)
                    token = RetryContext.set(retry_info)
                    try:
                        last_result = await func(*args, **kwargs)
                    finally:
                        RetryContext.reset(token)

                    # приводим к WithValid, но наружу возвращаем исходный result
                    wv = as_with_valid(last_result)
                    valid = getattr(wv, "valid", None)

                    if valid:
                        if hasattr(valid, "set_retry"):
                            valid.set_retry(current=attempt, maximum=quantity)
                        else:
                            valid.RETRY = retry_info

                    # нет валидатора или нет ошибок → успех, без ретраев
                    if not valid or not valid.has_errors():
                        return last_result

                    # есть ошибки: проверяем нужные ключи
                    has_key = False
                    try:
                        for e in getattr(valid, "ERRORS", []) or []:
                            if (e.key or "").upper() in keys:
                                has_key = True
                                break
                    except Exception:
                        has_key = False

                    # нет нужного ключа → не ретраим
                    if not has_key:
                        return last_result

                    # достигли лимита попыток → выходим
                    if attempt >= quantity:
                        return last_result

                    # ждём и пробуем ещё раз
                    await asyncio.sleep(interval)

            return wrapper

        return decorator
