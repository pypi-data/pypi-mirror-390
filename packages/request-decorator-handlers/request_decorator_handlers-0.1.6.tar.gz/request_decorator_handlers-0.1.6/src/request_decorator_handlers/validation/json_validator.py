from __future__ import annotations

from typing import Any, Dict, List, Union
import json
import re


class JSONValidator:
    """Универсальный валидатор и нормализатор JSON."""

    @staticmethod
    def normalize(
        data: Union[str, bytes, Dict[Any, Any], List[Any]],
        _depth: int = 0,
    ) -> Union[Dict[Any, Any], List[Any], None]:
        """
        Нормализует любой JSON в стандартный формат.

        Args:
            data: Сырые данные (строка, байты, dict, list)
            _depth: Глубина рекурсии (защита от бесконечной рекурсии)

        Returns:
            Нормализованный JSON (dict или list) или None если не удалось распарсить.
        """
        if _depth > 10:
            return None

        if isinstance(data, (dict, list)):
            return data

        if isinstance(data, bytes):
            try:
                data = data.decode("utf-8")
            except UnicodeDecodeError:
                data = data.decode("utf-8", errors="ignore")

        if not isinstance(data, str):
            data = str(data)

        data = data.strip()

        if not data:
            return None

        try:
            result = json.loads(data)
            if isinstance(result, str):
                return JSONValidator.normalize(result, _depth + 1)
            return result
        except json.JSONDecodeError:
            pass

        multiple_jsons = JSONValidator._extract_multiple_jsons(data)
        if multiple_jsons is not None:
            return multiple_jsons

        cleaned = JSONValidator._clean_json(data)
        if cleaned and cleaned != data:
            try:
                result = json.loads(cleaned)
                if isinstance(result, str):
                    return JSONValidator.normalize(result, _depth + 1)
                return result
            except json.JSONDecodeError:
                pass

        return None

    @staticmethod
    def _extract_multiple_jsons(data: str) -> Union[Dict[Any, Any], List[Any], None]:
        """Извлечь множественные JSON объекты из строки."""
        results: List[Any] = []

        bracket_count = 0
        start_idx = None

        for i, char in enumerate(data):
            if char == "{":
                if bracket_count == 0:
                    start_idx = i
                bracket_count += 1
            elif char == "}":
                bracket_count -= 1
                if bracket_count == 0 and start_idx is not None:
                    json_str = data[start_idx : i + 1]
                    try:
                        obj = json.loads(json_str)
                        results.append(obj)
                    except json.JSONDecodeError:
                        pass
                    start_idx = None

        if not results:
            bracket_count = 0
            start_idx = None

            for i, char in enumerate(data):
                if char == "[":
                    if bracket_count == 0:
                        start_idx = i
                    bracket_count += 1
                elif char == "]":
                    bracket_count -= 1
                    if bracket_count == 0 and start_idx is not None:
                        json_str = data[start_idx : i + 1]
                        try:
                            obj = json.loads(json_str)
                            results.append(obj)
                        except json.JSONDecodeError:
                            pass
                        start_idx = None

        if not results:
            return None

        if len(results) == 1:
            return results[0]

        return results

    @staticmethod
    def _clean_json(data: str) -> str:
        """Очистить JSON от комментариев и trailing commas."""
        data = re.sub(r"//.*?$", "", data, flags=re.MULTILINE)
        data = re.sub(r"/\*.*?\*/", "", data, flags=re.DOTALL)
        data = re.sub(r",\s*}", "}", data)
        data = re.sub(r",\s*]", "]", data)
        return data.strip()

    @staticmethod
    def safe_parse(data: Any, default: Any = None) -> Any:
        """
        Безопасный парсинг с fallback значением.

        Args:
            data: Данные для парсинга
            default: Значение по умолчанию если парсинг не удался

        Returns:
            Распарсенный JSON или default.
        """
        result = JSONValidator.normalize(data)
        return result if result is not None else default

    @staticmethod
    def is_valid(data: Any) -> bool:
        """Проверить валидность JSON."""
        return JSONValidator.normalize(data) is not None

