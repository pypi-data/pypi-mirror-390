# request-decorator-handlers

Набор декораторов и утилит для асинхронных HTTP-запросов. Библиотека помогает
логировать запросы, повторять их при ошибках, валидировать ответы и извлекать
нужные данные, не усложняя приложение бизнес-логикой.

- 🧪 Валидаторы с наглядным журналом ошибок (`Validator` и `ResponseHandler`)
- 📦 Парсеры (`Parser.JSON`, `Parser.HTML`, JSONPath/HTML helpers)
- 🪵 Цветное логирование (`RequestLogger`) с управлением через `loguru`
- 🧾 Отладчик (`RequestDebugger`) — коллекция невалидных ответов и уникальных JSON
- 🔁 Повторы запросов (`ResponseHandler.retry`)

## Установка

```bash
pip install request-decorator-handlers
```

## Основные импорты

```python
from request_decorator_handlers import (
    RequestLogger, RequestDebugger,
    ResponseHandler, Validator, ParserUtil,
)
```
## Быстрый старт

```python
import asyncio

from request_decorator_handlers import (
    RequestLogger, RequestDebugger,
    ResponseHandler, Validator, ParserUtil,
)
from curl_cffi import AsyncSession


# @RequestDebugger.debug(save_errors=True)
@ResponseHandler.retry(error_key="STATUS_CODE", quantity=3, interval=2.0)
@RequestLogger.log(action="GET_IP", log_level="success_error", show_body=True)
@ResponseHandler.handlers(
    Validator.status([312]),
    Validator.content_type("json"),
    Validator.JSON("$.query", exists=True, error_key="QUERY_EXISTS"),
)
async def fetch_ip(client: AsyncSession):
    return await client.get("http://ip-api.com/json")


async def main():
    async with AsyncSession() as client:
        result = await fetch_ip(client)
        print(result.valid.ERRORS, result.valid.PARSED)


asyncio.run(main())
```
## Требования к функциям

1. Декораторы ожидают асинхронные функции, возвращающие HTTP-ответ (любой тип с
   полями `status_code`, `headers`, `text/content` и т.п.) — например,
   `curl_cffi.AsyncResponse`, `httpx.Response`.
2. Декораторы `ResponseHandler.handlers(...)` и `ResponseHandler.retry(...)`
   оборачивают результат в `WithValid[Response]`. Если нужна строгая типизация:

   ```python
   from typing import Annotated
   from request_decorator_handlers import WithValid

   @ResponseHandler.handlers(...)
   async def fetch_user(...) -> WithValid[Response]:
       ...
   ```

3. Для интеграции со сторонними клиентов необходимо:
   - использовать их сессию/класс ответа;
   - возвращать исходный объект ответа (его обёртка `WithValid` создаётся сама).

## Быстрый пример

```python
import asyncio
from curl_cffi import AsyncSession
from request_decorator_handlers import (
    RequestLogger, RequestDebugger,
    ResponseHandler, Validator,
)

# Настраиваем loguru, потом включаем вывод библиотеки
from loguru import logger
logger.add(sys.stderr, format="{time} {level} {message}", colorize=True)
RequestLogger.enable()

@RequestDebugger.debug(save_errors=True)
@RequestLogger.log(action="GET_IP", log_level="success_error", show_body=True)
@ResponseHandler.handlers(
    Validator.status([200]),
    Validator.content_type("json"),
    Validator.JSON("$.query", exists=True, error_key="QUERY_EXISTS"),
)
@ResponseHandler.retry(error_key="STATUS_CODE", quantity=3, interval=2.0)
async def fetch_ip(client: AsyncSession):
    return await client.get("http://ip-api.com/json")

async def main():
    async with AsyncSession() as client:
        result = await fetch_ip(client)
        print(result.valid.ERRORS, result.valid.PARSED)

asyncio.run(main())
```

## RequestLogger — цветное логирование

Логгер работает через `loguru`. По умолчанию его вывод выключен, чтобы библиотека
не засоряла консоль. Включите его один раз после своей настройки `loguru`:

```python
from request_decorator_handlers import RequestLogger
RequestLogger.enable()
```

### Декоратор `RequestLogger.log`

```python
@RequestLogger.log(
    action: str,
    log_level: Literal["full", "success_error", "error_only"] = "full",
    show_body: bool = False,
    len_text: int | None = None,
    show_response_headers: bool = False,
    show_request_body: bool = False,
    show_request_headers: bool = False,
    enabled: bool = True,
)
```

- `action` — подпись (отображается в логе).
- `log_level` — объём сообщений:
  - `full` — старт, успехи, ошибки;
  - `success_error` — только финальные успехи + ошибки;
  - `error_only` — только ошибки.
- `show_body` — добавить блок с телом ответа (JSON/текст/байты).
- `show_request_body` / `show_request_headers` — показать исходные данные.
- `show_response_headers` — вывести заголовки из ответа.
- `len_text` — ограничение длины строковых значений.
- `enabled` — быстро отключить логирование для конкретной функции.

Дополнительно:

- `RequestLogger.disable()` — навсегда убрать вывод.
- `RequestLogger.muted()` — контекстный менеджер для временной тишины.

## ResponseHandler — валидация и ретраи

### Декоратор `ResponseHandler.handlers`

```python
@ResponseHandler.handlers(
    Validator.status([200]),
    Validator.headers(["content-type"]),
    ...
)
```

Каждый валидатор получает оригинальный ответ и объект `ValidationData`. Если
валидатор находит несоответствие, он добавляет запись об ошибке.

Функция, обёрнутая в `ResponseHandler.handlers`, возвращает `WithValid[Response]`:

```python
with_valid.valid.has_errors()  # bool
with_valid.valid.ERRORS        # список ValidationError
with_valid.valid.PARSED        # словарь с распарсенными значениями
with_valid.response            # оригинальный Response
```

### Доступные валидаторы

Все валидаторы находятся в `Validator` (из `request_decorator_handlers`):

| Валидатор | Назначение | Основные аргументы |
|-----------|------------|--------------------|
| `Validator.status(allowed)` | Проверить HTTP-код | `allowed: Iterable[int]` |
| `Validator.headers(required)` | Обязательные заголовки | список имён |
| `Validator.cookies(session, domain, required)` | Проверка cookie | сессия + домен + имена cookie |
| `Validator.content_type(expected)` | Формат ответа | `expected`: `"json"`, `"html"`, `"text"`, `"image"`, `"bytes"` |
| `Validator.REGEX(pattern, target="text")` | Совпадение по regex | `target`: `"text"`, `"json"`, `"content"`; `expect_match`; `save_to` |
| `Validator.JSON(path, ...)` | JSONPath-проверка | `exists`, `value`, `is_type`, `range_value`, `regex`, `words`, `error_key` |
| `Validator.HTML(selector, ...)` | HTML/XPath-проверка | `selector_type`, `extract`, `attr_name`, `exists`, фильтры |
| `Validator.cloudflare_blocked()` | Детектор Cloudflare-страниц | `keywords` (опционально), `error_key` |

#### Фильтры для JSON/HTML валидаторов

- `words`: список слов/фраз (хватает совпадения одного).
- `regex`, `regex_flags`: дополнительное регулярное выражение.
- `value`: точное совпадение.
- `is_type`: проверка типа (`int`, `str`, `bool` и т.п.).
- `range_value=(min, max)`: числовой диапазон.

#### Хранение парсенных значений

У многих валидаторов есть `save_to`, чтобы сохранить найденные значения в
`valid.PARSED`. Это касается `Validator.REGEX` и методов из `Parser` (см. ниже).

### JSON / HTML / REGEX парсеры

`Parser` (из `request_decorator_handlers.validation.response`) удобен, если
нужно извлечь данные и использовать их дальше:

```python
@ResponseHandler.handlers(
    Validator.status([200]),
    Parser.JSON("$.user.email", save_to="email"),
    Parser.HTML("span.username", words=["admin"], save_to="role"),
    Validator.REGEX(r'"token"\\s*:\\s*"([^"]+)"', target="json", save_to="token"),
)
```

### ResponseHandler.retry

```python
@ResponseHandler.retry(
    error_key: str | Iterable[str],
    quantity: int = 3,
    interval: float = 0.5,
    enabled: bool = True,
)
```

- `error_key` — одно имя или список имён ошибок из `ValidationData.ERRORS`.
- `quantity` — максимум попыток (включая первую).
- `interval` — задержка между повторами в секундах.
- `enabled` — общий переключатель.

Контекст ретрая сохраняется в `ValidationData.RETRY` (экземпляр `RetryInfo`).

## RequestDebugger — запись проблемных ответов

```python
@RequestDebugger.debug(
    enabled: bool = True,
    save_errors: bool = True,
    save_unique_structures: bool = False,
    debug_dir: str = "debug_request",
)
```

- `save_errors` — сохраняет JSON с ошибками и метаданными запроса.
- `save_unique_structures` — сохраняет структуру успешного ответа (для
  документов по API).
- `debug_dir` — корневая папка для записей.

Файлы структурируются по домену, пути и типу (`errors_json`, `unique_json`).


Результат будет обёрнут в `WithValid`, а извлечённые значения попадут в
`valid.PARSED`.


## Пример комплексной связки

```python
@RequestDebugger.debug(save_errors=True, debug_dir="debug")
@RequestLogger.log("FETCH_PROFILE", log_level="success_error", show_body=True)
@ResponseHandler.retry(error_key=["STATUS_CODE", "API_STATUS"], quantity=3, interval=2)
@ResponseHandler.handlers(
    Validator.status([200]),
    Validator.content_type("json"),
    Parser.JSON("$.profile.id", save_to="profile_id"),
    Validator.JSON("$.profile.is_active", value=True, error_key="USER_INACTIVE"),
    Validator.REGEX(r"\"token\":\"([^\"]+)\"", target="json", save_to="token"),
)
async def fetch_profile(session):
    return await session.get("https://api.example.com/profile")
```


Приятной отладки и чистых логов! 💙
