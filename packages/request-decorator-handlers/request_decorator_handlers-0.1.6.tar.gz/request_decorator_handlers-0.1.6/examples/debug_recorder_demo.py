"""
Тесты для декоратора RequestDebugger
"""

import asyncio

from bose_request import BossAsyncSessionCurlCffi

from request_handlers import LOG_ACTION, RequestDebugger, ResponseValidator, Validator


print("=" * 80)
print("ТЕСТИРОВАНИЕ ДЕКОРАТОРА RequestDebugger")
print("=" * 80)


# === Тест 1: Запись ошибок валидации ===
@RequestDebugger.debug(save_errors=True, save_unique_structures=False)
@ResponseValidator.status([200])  # Ожидаем 200, но получим 404
async def test_error_recording(client):
    """Этот запрос должен вернуть ошибку и записаться в errors_json"""
    return await client.get('https://httpbin.org/status/404')


# === Тест 2: Запись уникальных структур ===
@RequestDebugger.debug(save_errors=False, save_unique_structures=True)
@ResponseValidator.status([200])
async def test_unique_structure_1(client):
    """Первая структура JSON от /get"""
    return await client.get('https://httpbin.org/get')


@RequestDebugger.debug(save_errors=False, save_unique_structures=True)
@ResponseValidator.status([200])
async def test_unique_structure_2(client):
    """Вторая структура JSON от /get (должна быть такой же, не записывается)"""
    return await client.get('https://httpbin.org/get')


@RequestDebugger.debug(save_errors=False, save_unique_structures=True)
@ResponseValidator.status([200])
async def test_unique_structure_3(client):
    """Третья структура JSON от /post (другая структура, записывается)"""
    return await client.post('https://httpbin.org/post', json={"test": "data"})


# === Тест 3: Запись и ошибок, и уникальных структур ===
@RequestDebugger.debug(save_errors=True, save_unique_structures=True)
@ResponseValidator.status([200, 201])
@ResponseValidator.headers(["x-nonexistent-header"])  # Несуществующий заголовок -> ошибка
async def test_both_modes(client):
    """Тест с ошибкой валидации (должен записаться в errors_json)"""
    return await client.get('https://httpbin.org/get')


# === Тест 4: Разные endpoints -> разные папки ===
@RequestDebugger.debug(save_errors=False, save_unique_structures=True)
@ResponseValidator.status([200])
async def test_different_endpoint_1(client):
    """Другой endpoint -> другая папка"""
    return await client.get('https://httpbin.org/uuid')


@RequestDebugger.debug(save_errors=False, save_unique_structures=True)
@ResponseValidator.status([200])
async def test_different_endpoint_2(client):
    """Еще один endpoint"""
    return await client.get('https://httpbin.org/ip')


async def main():
    async with BossAsyncSessionCurlCffi() as client:

        print("\n--- Тест 1: Запись ошибки (404 вместо 200) ---")
        try:
            await test_error_recording(client)
        except Exception:
            pass  # Игнорируем ошибки валидации

        print("\n--- Тест 2: Уникальные структуры ---")
        print("  2.1: Первый запрос к /get (новая структура - запишется)")
        await test_unique_structure_1(client)

        print("  2.2: Второй запрос к /get (та же структура - не запишется)")
        await test_unique_structure_2(client)

        print("  2.3: Запрос к /post (другая структура - запишется)")
        await test_unique_structure_3(client)

        print("\n--- Тест 3: Ошибка + уникальная структура ---")
        await test_both_modes(client)

        print("\n--- Тест 4: Разные endpoints ---")
        await test_different_endpoint_1(client)
        await test_different_endpoint_2(client)

        print("\n" + "=" * 80)
        print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        print("=" * 80)
        print("\nПроверьте папку debug_request/ для просмотра результатов:")
        print("  - debug_request/httpbin.org/status_404/errors_json/")
        print("  - debug_request/httpbin.org/get/errors_json/")
        print("  - debug_request/httpbin.org/get/unique_json/")
        print("  - debug_request/httpbin.org/post/unique_json/")
        print("  - debug_request/httpbin.org/uuid/unique_json/")
        print("  - debug_request/httpbin.org/ip/unique_json/")


if __name__ == "__main__":
    asyncio.run(main())
