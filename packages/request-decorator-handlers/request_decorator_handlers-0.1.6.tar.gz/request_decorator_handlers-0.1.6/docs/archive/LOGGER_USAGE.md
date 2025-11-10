# RequestLogger - Улучшенный декоратор для логирования HTTP запросов

## Описание

`RequestLogger.log()` - декоратор для логирования HTTP запросов с поддержкой отображения тела и заголовков запроса/ответа.

## Параметры

- **action** (str): Название действия для логирования (например: `LOG_ACTION.AUTH.LOGIN`)
- **log_level** (Literal["full", "success_error", "error_only"]): Уровень логирования
  - `"full"` - логировать старт, успех и ошибки
  - `"success_error"` - логировать только успех и ошибки (без старта)
  - `"error_only"` - логировать только ошибки
- **show_body** (bool): Показывать тело ответа (по умолчанию: False)
- **len_text** (int): Максимальная длина отображаемого текста (по умолчанию: 150)
- **show_response_headers** (bool): Показывать заголовки ответа (по умолчанию: False)
- **show_request_body** (bool): Показывать тело запроса (по умолчанию: False) - *ограничено клиентом*
- **show_request_headers** (bool): Показывать заголовки запроса (по умолчанию: False)
- **enabled** (bool): Включить/выключить логирование (по умолчанию: True)

## Примеры использования

### 1. Базовое логирование

```python
from action import LOG_ACTION
from test_dto import RequestLogger, ResponseValidator

@RequestLogger.log(LOG_ACTION.FETCH.PROFILE, log_level="success_error")
@ResponseValidator.status([200])
async def get_profile(client):
    return await client.get('https://api.example.com/profile')
```

### 2. Логирование с телом ответа

```python
@RequestLogger.log(
    LOG_ACTION.FETCH.DATA,
    log_level="success_error",
    show_body=True,
    len_text=100  # Обрезать до 100 символов
)
@ResponseValidator.status([200])
async def get_data(client):
    return await client.get('https://api.example.com/data')
```

**Вывод:**
```
22:13:38 | ✓ SUCCESS   1.108с |-> FETCH.DATA          | api.example.com/data         [200]
  └─ response body: {"status": "ok", "data": [...]}...
```

### 3. Логирование с заголовками ответа

```python
@RequestLogger.log(
    LOG_ACTION.FETCH.PROFILE,
    log_level="success_error",
    show_response_headers=True
)
@ResponseValidator.status([200])
async def get_with_headers(client):
    return await client.get('https://api.example.com/data')
```

**Вывод:**
```
22:13:38 | ✓ SUCCESS   0.395с |-> FETCH.PROFILE       | api.example.com/data         [200]
  └─ response headers: date: Fri, 31 Oct 2025 20:13:38 GMT, content-type: application/json, ...
```

### 4. Логирование с заголовками запроса

```python
@RequestLogger.log(
    LOG_ACTION.SEND.DATA,
    log_level="success_error",
    show_request_headers=True
)
@ResponseValidator.status([200])
async def send_with_custom_headers(client):
    return await client.get(
        'https://api.example.com/data',
        headers={
            "User-Agent": "MyBot/1.0",
            "X-API-Key": "secret-key",
            "Accept": "application/json"
        }
    )
```

**Вывод:**
```
22:13:40 | ✓ SUCCESS   0.761с |-> SEND.DATA           | api.example.com/data         [200]
  └─ request headers: user-agent: MyBot/1.0, x-api-key: secret-key, accept: application/json
```

### 5. Полное логирование (все опции)

```python
@RequestLogger.log(
    LOG_ACTION.SEND.FORM,
    log_level="full",  # Логировать старт + результат
    show_body=True,
    show_response_headers=True,
    show_request_body=True,
    show_request_headers=True,
    len_text=150
)
@ResponseValidator.status([200])
async def full_logging_example(client):
    return await client.post(
        'https://api.example.com/submit',
        json={"action": "submit", "data": "test"},
        headers={"Content-Type": "application/json", "X-API-Key": "secret"}
    )
```

**Вывод:**
```
22:16:33 | • DEBUG     0.000с |-> SEND.FORM           | N/A                          [000]
22:16:34 | ✓ SUCCESS   1.823с |-> SEND.FORM           | api.example.com/submit       [200]
  ├─ request headers: content-type: application/json, x-api-key: secret
  ├─ response headers: date: Fri, 31 Oct 2025 20:16:34 GMT, content-type: application/json, ...
  └─ response body: {"status": "ok", "result": {...}}...
```

### 6. Только ошибки

```python
@RequestLogger.log(
    LOG_ACTION.FETCH.PROFILE,
    log_level="error_only"  # Логировать только ошибки
)
@ResponseValidator.status([200, 201])
async def check_status(client):
    return await client.get('https://api.example.com/status/404')
```

### 7. Отключить логирование

```python
@RequestLogger.log(LOG_ACTION.FETCH.BALANCE, enabled=False)
@ResponseValidator.status([200])
async def silent_request(client):
    return await client.get('https://api.example.com/balance')
```

## Особенности

### Цветовое кодирование времени

- **Серый** (< 15 сек): Быстрый ответ
- **Темно-красный** (15-35 сек): Медленный ответ
- **Красный** (> 35 сек): Очень медленный ответ

### Цветовое кодирование статус-кода

- **Зеленый** (2xx): Успех
- **Фиолетовый** (3xx): Редирект
- **Красный** (4xx, 5xx): Ошибка

### Отображение деталей

Детали запроса/ответа отображаются с правильными символами:
- `├─` - для промежуточных элементов
- `└─` - для последнего элемента

Порядок отображения:
1. Request headers (зеленый цвет)
2. Request body (зеленый цвет)
3. Response headers (серый цвет)
4. Response body (серый цвет)

### Ограничения длины

Параметр `len_text` ограничивает длину отображаемого текста:
- Для тела ответа
- Для тела запроса
- Текст обрезается с добавлением `...`

Заголовки показываются только первые 5, остальные - `... (+N more)`

## Ограничения

**Request body:** Из-за ограничений клиента `curl_cffi/bose_request`, тело запроса не доступно через `response.request.body`. Параметр `show_request_body` может не работать для некоторых клиентов.

## Комбинирование с валидаторами

Декоратор отлично работает с валидаторами:

```python
@RequestLogger.log(
    LOG_ACTION.AUTH.LOGIN,
    log_level="full",
    show_body=True,
    show_response_headers=True,
    show_request_headers=True
)
@ResponseValidator.status([200])
@ResponseValidator.headers(["content-type"])
@ResponseValidator.content_type("json")
async def login(client):
    return await client.post(
        'https://api.example.com/login',
        json={"username": "user", "password": "pass"}
    )
```

## Примеры тестирования

Запустите демо-тесты:
```bash
python test_logger_demo.py
```

Вывод покажет все возможности улучшенного декоратора логов.
