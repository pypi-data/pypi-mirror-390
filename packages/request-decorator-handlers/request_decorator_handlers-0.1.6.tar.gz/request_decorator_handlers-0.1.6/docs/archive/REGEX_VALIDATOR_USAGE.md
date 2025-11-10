# Regex Validator - Документация

## Описание

`ResponseValidator.regex()` - декоратор для валидации HTTP response через регулярные выражения.

## Параметры

- **pattern** (str | Pattern): Регулярное выражение (строка или скомпилированный паттерн)
- **target** (Literal['text', 'json', 'content']): Где искать паттерн
  - `'text'` - в response.text (по умолчанию)
  - `'json'` - в JSON строке (response.json())
  - `'content'` - в response.content (байты декодируются в UTF-8)
- **flags** (int): Флаги regex (например: `re.IGNORECASE`, `re.MULTILINE`, `re.DOTALL`)
- **error_key** (str): Ключ для сохранения ошибки валидации (по умолчанию `"REGEX_VALIDATION_ERROR"`)
- **save_to** (Optional[str]): Если указано, найденные совпадения сохраняются в `response.PARSED[save_to]`
- **expect_match** (bool):
  - `True` - ожидаем найти совпадение (ошибка если не найдено)
  - `False` - НЕ ожидаем найти совпадение (ошибка если найдено)

## Примеры использования

### 1. Извлечь email из HTML

```python
from validator.parse import ResponseValidator

@ResponseValidator.regex(
    r'\b[\w.-]+@[\w.-]+\.\w+\b',
    target='text',
    save_to='email',
    error_key='EMAIL_NOT_FOUND'
)
async def fetch_page(session):
    return await session.get('https://example.com')

# Использование
response = await fetch_page(session)
if hasattr(response, 'PARSED') and 'email' in response.PARSED:
    print(f"Email: {response.PARSED['email']}")
```

### 2. Проверить что НЕТ ошибок в ответе

```python
@ResponseValidator.regex(
    r'error|exception|fail',
    flags=re.IGNORECASE,
    expect_match=False,  # НЕ ожидаем найти
    error_key='ERROR_IN_RESPONSE'
)
async def fetch_safe_data(session):
    return await session.get('https://api.example.com/data')

# Если найдется слово "error", будет ошибка валидации
response = await fetch_safe_data(session)
if response.has_validation_errors():
    print(f"Ошибки: {response.get_validation_errors()}")
```

### 3. Извлечь токен из JSON с группой захвата

```python
@ResponseValidator.regex(
    r'"access_token":\s*"([^"]+)"',
    target='json',
    save_to='access_token',
    error_key='TOKEN_NOT_FOUND'
)
async def login(session):
    return await session.post('https://api.example.com/login',
                             json={'username': 'user', 'password': 'pass'})

response = await login(session)
if hasattr(response, 'PARSED'):
    token = response.PARSED['access_token']
    print(f"Token: {token}")
```

### 4. Извлечь несколько значений

```python
@ResponseValidator.regex(
    r'<h2>([^<]+)</h2>',
    save_to='headings'
)
async def fetch_html(session):
    return await session.get('https://example.com')

# Если найдено несколько совпадений, вернется список
response = await fetch_html(session)
if hasattr(response, 'PARSED'):
    headings = response.PARSED['headings']  # ['Heading 1', 'Heading 2', ...]
```

### 5. Комплексная валидация

```python
@ResponseValidator.status([200])
@ResponseValidator.headers(['Content-Type'])
@ResponseValidator.regex(r'<title>([^<]+)</title>', save_to='title')
@ResponseValidator.regex(r'<meta name="csrf-token" content="([^"]+)"', save_to='csrf_token')
@ResponseValidator.regex(r'error', flags=re.IGNORECASE, expect_match=False)
async def fetch_html_page(session):
    return await session.get('https://example.com')

response = await fetch_html_page(session)

# Доступ к извлеченным данным
print(f"Title: {response.PARSED['title']}")
print(f"CSRF Token: {response.PARSED['csrf_token']}")

# Проверка ошибок
if response.has_validation_errors():
    print(f"Ошибки валидации: {response.get_validation_errors()}")
```

### 6. Использование флагов regex

```python
import re

@ResponseValidator.regex(
    r'warning|error',
    flags=re.IGNORECASE | re.MULTILINE,
    save_to='issues'
)
async def fetch_logs(session):
    return await session.get('https://example.com/logs')
```

## Работа с результатами

### ValidatedResponse методы

```python
# Проверить наличие ошибок
if response.has_validation_errors():
    # Получить словарь всех ошибок
    errors = response.get_validation_errors()
    # {'ERROR_IN_RESPONSE': 'Pattern not found...', ...}

# Доступ к спарсенным данным
if hasattr(response, 'PARSED'):
    data = response.PARSED  # {'email': '...', 'token': '...'}
```

## Особенности работы

1. **Группы захвата**: Если в паттерне есть группы `()`, будет возвращена первая группа
   ```python
   r'<title>([^<]+)</title>'  # Вернет только содержимое между тегами
   ```

2. **Множественные совпадения**: Если найдено несколько совпадений, вернется список
   ```python
   r'\b[\w.-]+@[\w.-]+\.\w+\b'  # Найдет все email на странице
   # response.PARSED['emails'] = ['email1@test.com', 'email2@test.com']
   ```

3. **Комбинирование декораторов**: Можно использовать несколько regex валидаторов на одной функции
   ```python
   @ResponseValidator.regex(pattern1, save_to='field1')
   @ResponseValidator.regex(pattern2, save_to='field2')
   async def fetch_data(session):
       ...
   ```

4. **Обработка ошибок**: Любые исключения при обработке regex перехватываются и сохраняются как ошибка валидации

## Тестирование

Запустить тесты:
```bash
python test_regex_validator.py
```

Все тесты проверяют различные сценарии использования regex валидатора.
