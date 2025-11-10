# Улучшения RequestLogger - Итоговая документация

## Что было улучшено

### 1. **Умное отображение тела ответа (response body)**

Теперь декоратор умно извлекает тело ответа в следующем приоритете:
- **JSON** (с форматированием indent=2) → если response.json() работает
- **Text** → если есть response.text
- **Content** → если есть response.content (декодируется как UTF-8)

**Преимущества:**
- Автоматическое определение формата
- Красивое форматирование JSON с отступами
- Обрезка по len_text с добавлением `...`

**Пример вывода:**
```
└─ response body: {
  "args": {},
  "data": "{\"action\":\"submit\",\"user_id\":12345}",
  "headers": {
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/json",
    ...
  }
}
```

### 2. **Полное отображение заголовков**

Заголовки теперь отображаются **полностью** в формате Python dict, а не только первые 5.

**Было:**
```
response headers: date: ..., content-type: ..., ... (+3 more)
```

**Стало:**
```
response headers: {'date': 'Fri, 31 Oct 2025 20:29:32 GMT', 'content-type': 'application/json', 'content-length': '245', 'server': 'gunicorn/19.9.0', 'access-control-allow-origin': '*', 'access-control-allow-credentials': 'true'}
```

### 3. **Отображение тела запроса (request body)**

Добавлена поддержка отображения тела запроса с умным форматированием:
- **Dict** → форматируется как JSON с indent=2
- **String** → отображается как есть
- **Bytes** → конвертируется в строку

**Ограничение:** Работает только если `json` или `data` передаются как именованные параметры в декорируемую функцию:

```python
# ✅ Работает
@RequestLogger.log(action, show_request_body=True)
async def request(client, json_data):
    return await client.post(url, json=json_data)  # json из параметра

# ❌ Не работает (тело создается внутри функции)
@RequestLogger.log(action, show_request_body=True)
async def request(client):
    json_data = {"key": "value"}  # создано внутри
    return await client.post(url, json=json_data)
```

### 4. **Отображение заголовков запроса (request headers)**

Заголовки запроса извлекаются из:
1. `kwargs['headers']` - если переданы в декорируемую функцию
2. `response.request.headers` - после выполнения запроса ✅

**Работает в обоих случаях!**

### 5. **Параметр len_text**

Добавлен параметр для контроля длины отображаемого текста (по умолчанию: 150):

```python
@RequestLogger.log(
    action,
    show_body=True,
    len_text=300  # Обрезать до 300 символов
)
```

## Параметры декоратора

```python
@RequestLogger.log(
    action: str,
    log_level: Literal["full", "success_error", "error_only"] = "full",
    show_body: bool = False,              # Показывать тело ответа
    len_text: int = 150,                  # Макс. длина текста
    show_response_headers: bool = False,  # Показывать заголовки ответа
    show_request_body: bool = False,      # Показывать тело запроса*
    show_request_headers: bool = False,   # Показывать заголовки запроса
    enabled: bool = True,
)
```

## Примеры использования

### Базовый пример с телом ответа

```python
@RequestLogger.log(
    LOG_ACTION.FETCH.DATA,
    show_body=True,
    len_text=200
)
@ResponseValidator.status([200])
async def get_data(client):
    return await client.get('https://api.example.com/data')
```

**Вывод:**
```
22:29:31 | ✓ SUCCESS   2.087с |-> FETCH.DATA          | api.example.com/data         [200]
  └─ response body: {
  "status": "success",
  "data": [...]
}
```

### С заголовками ответа

```python
@RequestLogger.log(
    LOG_ACTION.FETCH.PROFILE,
    show_response_headers=True
)
@ResponseValidator.status([200])
async def get_profile(client):
    return await client.get('https://api.example.com/profile')
```

**Вывод:**
```
22:29:32 | ✓ SUCCESS   0.982с |-> FETCH.PROFILE       | api.example.com/profile      [200]
  └─ response headers: {'date': '...', 'content-type': 'application/json', ...}
```

### С заголовками запроса

```python
@RequestLogger.log(
    LOG_ACTION.SEND.DATA,
    show_request_headers=True
)
@ResponseValidator.status([200])
async def send_data(client):
    return await client.post(
        'https://api.example.com/data',
        headers={
            "Authorization": "Bearer token123",
            "X-API-Key": "secret"
        }
    )
```

**Вывод:**
```
22:29:34 | ✓ SUCCESS   0.392с |-> SEND.DATA           | api.example.com/data         [200]
  └─ request headers: {'authorization': 'Bearer token123', 'x-api-key': 'secret'}
```

### Полное логирование (все опции)

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
        'https://api.example.com/submit',
        json={"action": "submit", "data": "test"},
        headers={"Authorization": "Bearer token"}
    )
```

**Вывод:**
```
22:29:34 | • DEBUG     0.000с |-> SEND.FORM           | N/A                          [000]
22:29:35 | ✓ SUCCESS   1.135с |-> SEND.FORM           | api.example.com/submit       [200]
  ├─ request headers: {'authorization': 'Bearer token'}
  ├─ response headers: {'date': '...', 'content-type': 'application/json', ...}
  └─ response body: {
  "status": "ok",
  "result": {...}
}
```

## Форматирование вывода

### Правильное использование символов дерева

Детали отображаются с корректными символами:
- `├─` - для промежуточных элементов
- `└─` - для последнего элемента

**Порядок отображения:**
1. Request headers (зеленый)
2. Request body (зеленый)
3. Response headers (серый)
4. Response body (серый)

### Цветовое кодирование

**Request (зеленый):**
- Request headers
- Request body

**Response (серый):**
- Response headers
- Response body

## Технические детали

### Метод _extract_response_body()

```python
def _extract_response_body(response_obj, len_text):
    """Умное извлечение: json -> text -> content"""
    # 1. Попробовать JSON (приоритет)
    try:
        json_data = response_obj.json()
        return json.dumps(json_data, ensure_ascii=False, indent=2)[:len_text]
    except: pass

    # 2. Попробовать text
    try:
        return response_obj.text[:len_text]
    except: pass

    # 3. Попробовать content
    try:
        return response_obj.content.decode('utf-8')[:len_text]
    except: pass

    return None
```

### Метод _format_request_body()

```python
def _format_request_body(request_body, len_text):
    """Форматирование тела запроса"""
    # Если dict - форматировать как JSON
    if isinstance(request_body, dict):
        return json.dumps(request_body, ensure_ascii=False, indent=2)[:len_text]

    # Иначе как строка
    return str(request_body)[:len_text]
```

## Ограничения

1. **Request body** - работает только если `json`/`data` передаются как параметры декорируемой функции
2. **Длина заголовков** - показываются полностью (может быть длинным)
3. **Кодировка content** - декодируется как UTF-8 с игнорированием ошибок

## Запуск тестов

```bash
# Базовые тесты
python test_logger_demo.py

# Полные тесты
python test_logger_full.py

# Все тесты декоратора
python test_dto.py
```

## Итог

Все улучшения успешно реализованы! ✅

- ✅ Умное отображение body (json/text/content)
- ✅ Заголовки полностью в формате dict
- ✅ Поддержка отображения request body
- ✅ Поддержка отображения request headers
- ✅ Параметр len_text для контроля длины
- ✅ Правильное форматирование с символами ├─ и └─
- ✅ Цветовое кодирование (request=зеленый, response=серый)
