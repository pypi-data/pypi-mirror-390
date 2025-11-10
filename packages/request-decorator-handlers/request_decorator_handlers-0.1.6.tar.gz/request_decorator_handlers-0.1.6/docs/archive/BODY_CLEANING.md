# Очистка response body - Документация

## Что было улучшено

### Проблема

При отображении `response body` показывались ненужные данные:
- **headers** - заголовки это не тело, они отображаются отдельно
- **Пустые поля** - `"args": {}`, `"files": {}`, `"form": {}` и т.д.

**Было:**
```json
{
  "args": {},
  "data": "{...}",
  "files": {},
  "form": {},
  "headers": {
    "Accept-Encoding": "gzip, deflate, br",
    "Authorization": "Bearer token123",
    ...
  },
  "json": {...},
  "origin": "31.202.139.105",
  "url": "https://httpbin.org/post"
}
```

### Решение

Добавлен метод `_clean_body_json()` который:
1. ✅ Удаляет поле `"headers"` (это не тело)
2. ✅ Удаляет все пустые поля:
   - Пустые dict: `{}`
   - Пустые list: `[]`
   - Пустые string: `""`
   - `None` значения
3. ✅ Работает рекурсивно для вложенных структур

**Стало:**
```json
{
  "data": "{\"action\":\"create_user\",...}",
  "json": {
    "action": "create_user",
    "metadata": {
      "source": "api",
      "timestamp": "2025-10-31"
    },
    "user_data": {
      "age": 30,
      "email": "john@example.com",
      "name": "John Doe"
    }
  },
  "origin": "31.202.139.105",
  "url": "https://httpbin.org/post"
}
```

## Реализация

### Метод _clean_body_json()

```python
@staticmethod
def _clean_body_json(data: Any) -> Any:
    """Очистка JSON от headers и пустых полей"""
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            # Пропускаем поле headers (это не тело)
            if key == "headers":
                continue

            # Рекурсивно очищаем вложенные структуры
            cleaned_value = _Msg._clean_body_json(value)

            # Пропускаем пустые значения
            if cleaned_value in ({}, [], "", None):
                continue

            cleaned[key] = cleaned_value
        return cleaned

    elif isinstance(data, list):
        cleaned = [_Msg._clean_body_json(item) for item in data]
        # Убираем пустые элементы
        return [item for item in cleaned if item not in ({}, [], "", None)]

    else:
        return data
```

### Интеграция в _extract_response_body()

```python
@staticmethod
def _extract_response_body(response_obj: Any, len_text: int) -> str | None:
    """Умное извлечение тела ответа: пробуем json -> text -> content"""
    # ...
    try:
        json_data = response_obj.json()

        # Очищаем от headers и пустых полей
        cleaned_data = _Msg._clean_body_json(json_data)

        # Если после очистки осталось что-то - форматируем
        if cleaned_data:
            body_str = json.dumps(cleaned_data, ensure_ascii=False, indent=2)
            if len(body_str) > len_text:
                return body_str[:len_text] + "..."
            return body_str
    except Exception:
        pass
    # ...
```

## Примеры использования

### Пример 1: GET запрос

**Response от httpbin.org/get:**
```json
{
  "args": {},
  "headers": {...},
  "origin": "31.202.139.105",
  "url": "https://httpbin.org/get"
}
```

**После очистки:**
```json
{
  "origin": "31.202.139.105",
  "url": "https://httpbin.org/get"
}
```

### Пример 2: POST запрос с JSON

**Response от httpbin.org/post:**
```json
{
  "args": {},
  "data": "{\"username\":\"test\",\"password\":\"secret\"}",
  "files": {},
  "form": {},
  "headers": {...},
  "json": {
    "username": "test",
    "password": "secret"
  },
  "origin": "31.202.139.105",
  "url": "https://httpbin.org/post"
}
```

**После очистки:**
```json
{
  "data": "{\"username\":\"test\",\"password\":\"secret\"}",
  "json": {
    "username": "test",
    "password": "secret"
  },
  "origin": "31.202.139.105",
  "url": "https://httpbin.org/post"
}
```

## Логирование

### Полный пример с очищенным body

```python
@RequestLogger.log(
    LOG_ACTION.SEND.FORM,
    log_level="full",
    show_body=True,
    show_response_headers=True,
    show_request_headers=True,
    len_text=400
)
@ResponseValidator.status([200])
async def submit_form(client):
    return await client.post(
        'https://httpbin.org/post',
        json={"action": "submit", "user_id": 12345},
        headers={"Authorization": "Bearer token"}
    )
```

**Вывод:**
```
22:39:44 | ✓ SUCCESS   1.457с |-> SEND.FORM           | httpbin.org/post              [200]
  ├─ request headers: {'content-type': 'application/json', 'authorization': 'Bearer token', ...}
  ├─ response headers: {'date': '...', 'content-type': 'application/json', ...}
  └─ response body: {
  "data": "{\"action\":\"submit\",\"user_id\":12345}",
  "json": {
    "action": "submit",
    "user_id": 12345
  },
  "origin": "31.202.139.105",
  "url": "https://httpbin.org/post"
}
```

**Обратите внимание:**
- ❌ Нет `"headers"` в body (они показаны отдельно)
- ❌ Нет `"args": {}`
- ❌ Нет `"files": {}`
- ❌ Нет `"form": {}`
- ✅ Только актуальное содержимое

## Преимущества

1. **Чище вывод** - нет мусора в виде пустых полей
2. **Меньше текста** - сокращается длина логов
3. **Понятнее** - видно только то что реально есть
4. **Headers отдельно** - заголовки не смешиваются с телом
5. **Рекурсивная очистка** - работает для вложенных структур

## Что удаляется

### Удаляемые поля:
- `"headers"` - всегда удаляется (показывается отдельно)
- `"args": {}` - если пустой dict
- `"files": {}` - если пустой dict
- `"form": {}` - если пустой dict
- Любое поле с `{}`, `[]`, `""` или `None`

### Что остается:
- `"data"` - если не пустое
- `"json"` - если не пустое
- `"origin"` - если не пустое
- `"url"` - если не пустое
- Любое поле с непустым значением

## Тестирование

Запустите тесты:
```bash
python test_logger_demo.py
python test_logger_full.py
```

## Совместимость

Очистка работает только для JSON responses. Для text/content очистка не применяется (возвращается как есть).

## Итог

✅ Response body теперь показывает только актуальное содержимое
✅ Заголовки не дублируются (показываются отдельно)
✅ Нет пустых полей в выводе
✅ Чище и понятнее логи
