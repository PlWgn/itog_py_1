import asyncio
import ssl
from abc import ABC, abstractmethod
try:
    import aiohttp
    import certifi
except ImportError:
    print('Не установлены библиотеки aiohttp и certifi. Чтобы установить используйте pip3 install -U aiohttp certifi')
    raise SystemExit

class Model(ABC):
    url = 'https://dummyjson.com/products'

    @abstractmethod
    async def download(self, categories:list):
        pass

    @abstractmethod
    def to_dict(self, data:list):
        pass

class Loader(Model):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def split_categories(self, categories:list, batch_size:int):
        if batch_size < 1:
            raise ValueError(f'Размер пакета не может быть меньше 1: {batch_size}')
        return [categories[index:index + batch_size] for index in range(0, len(categories), batch_size)]

    async def get_json(self, session:aiohttp.ClientSession, url:str, default):
        try:
            async with session.get(url, params={'limit': 0}) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as err:
            print(err)
        except asyncio.TimeoutError:
            print(f'Превышено время ожидания: {url}')
        return default

    async def download(self, categories:list = None, batch_size:int = 5):
        data = []
        timeout = aiohttp.ClientTimeout(total=10)
        # сертификаты берутся из certifi, чтобы проверка SSL работала на любой системе
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_context)

        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            # если категории не переданы, то загружаем все категории сервиса
            if categories is None:
                categories = await self.get_json(session, f'{self.url}/category-list', [])

            for batch in self.split_categories(categories, batch_size):
                tasks = [self.get_json(session, f'{self.url}/category/{category}', {}) for category in batch]
                data.extend(await asyncio.gather(*tasks))

        return self.to_dict(data)

    def to_dict(self, data:list):
        result = {}

        for item in data:
            for product in item.get('products', []):
                category = product.get('category', 'Неизвестная')
                result.setdefault(category, []).append(product)

        return result
