try:
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
except ImportError:
    print('Не установлены библиотеки sqlalchemy, greenlet и aiosqlite. Чтобы установить используйте pip3 install -U sqlalchemy greenlet aiosqlite')
    raise SystemExit
from models import Base

class Database:
    def __init__(self, db_name:str = 'catalog.db', user:str = None, password:str = None, host:str = None, port:int = 5432):
        db_name = str(db_name).strip() or 'catalog.db'

        # если переданы данные авторизации, то подключаемся к PostgreSQL, иначе к SQLite
        if user and password and host:
            self.__url = f'postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}'
        else:
            self.__url = f'sqlite+aiosqlite:///{db_name}'

        self.__engine = create_async_engine(self.__url)
        self.__session_maker = async_sessionmaker(bind=self.__engine, expire_on_commit=False)

    @property
    def engine(self):
        return self.__engine

    async def create_tables(self):
        # create_all создает только те таблицы, которых еще нет в базе
        async with self.__engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    def get_session(self):
        return self.__session_maker()

    async def close(self):
        await self.__engine.dispose()
