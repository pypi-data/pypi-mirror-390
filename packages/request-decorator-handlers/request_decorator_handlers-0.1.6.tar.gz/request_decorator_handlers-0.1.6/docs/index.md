# request-handlers toolkit

Набор декораторов и утилит поверх `requests`/`curl_cffi`/`boss-request` для
одинаковым образом оформленных запросов:

- `request_handlers.RequestLogger` — логирование действий с цветными бейджами и
  подсветкой ошибок.
- `request_handlers.ResponseValidator` — набор валидаторов (статусы, заголовки,
  content-type, regex и т.д.).
- `request_handlers.parsing.JSONPathParser` и `HTMLParser` — извлечение данных из
  ответов.
- `request_handlers.RequestDebugger` — запись проблемных запросов и уникальных структур.

## Быстрый старт

```python
import asyncio
from request_handlers import RequestLogger, ResponseValidator, LOG_ACTION
from request_handlers.decorators import RequestDebugger

@RequestDebugger.debug(save_errors=True)
@RequestLogger.log(LOG_ACTION.FETCH.PROFILE, show_body=True)
@ResponseValidator.status([200])
async def fetch_profile(client):
    return await client.get("https://httpbin.org/get")

async def main():
    async with BossAsyncSessionCurlCffi() as client:
        await fetch_profile(client)

asyncio.run(main())
```

## Валидация

```python
from request_handlers import ResponseValidator

@ResponseValidator.status([200])
@ResponseValidator.headers(["content-type"])
@ResponseValidator.regex(r"token", expect_match=False)
async def call_api(session):
    return await session.get("https://api.example.com/health")
```

## Парсинг JSON

```python
from request_handlers import JSONPathParser

@JSONPathParser.parse_field("$.user.email", "email")
async def load_user(session):
    return await session.get("https://api.example.com/me")
```

Больше примеров — в каталоге `examples/`.
