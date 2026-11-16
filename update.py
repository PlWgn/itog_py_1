import asyncio
import sys
import time
from database import Database
from service import update_data

async def main(categories:list):
    database = Database('catalog.db')
    try:
        return await update_data(database, categories)
    finally:
        await database.close()

# категории можно передать через пробел, без аргументов загружаются все категории
categories = sys.argv[1:] or None

start = time.perf_counter()
added_count, updated_count = asyncio.run(main(categories))
end = time.perf_counter()

print(f'Добавлено товаров: {added_count}, обновлено товаров: {updated_count}')
print(f'Время обновления: {round(end - start, 2)} сек.')
