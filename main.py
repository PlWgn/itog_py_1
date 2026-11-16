import time
from contextlib import asynccontextmanager
try:
    from fastapi import FastAPI, HTTPException
except ImportError:
    print('Не установлена библиотека fastapi. Чтобы установить используйте pip3 install -U fastapi uvicorn')
    raise SystemExit
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from database import Database
from models import Category, Brand, Product
from service import update_data

CACHE_SECONDS = 60
cache = {}

database = Database('catalog.db')

def get_cache(key:str):
    item = cache.get(key)
    if item is not None and time.time() - item['time'] < CACHE_SECONDS:
        return item['data']
    return None

def set_cache(key:str, data):
    cache[key] = {'data': data, 'time': time.time()}
    return data

def product_to_dict(product:Product):
    brand_name = None
    if product.brand is not None:
        brand_name = product.brand.name

    result = product.to_dict()
    del result['category_id']
    del result['brand_id']
    result['category'] = product.category.name
    result['brand'] = brand_name
    return result

async def select_products(session, condition = None):
    query = select(Product).options(joinedload(Product.category), joinedload(Product.brand)).order_by(Product.id)
    if condition is not None:
        query = query.where(condition)
    products = (await session.scalars(query)).all()
    return [product_to_dict(product) for product in products]

@asynccontextmanager
async def lifespan(app:FastAPI):
    # если таблиц нет, то они создаются, а пустая база заполняется данными из DummyJSON
    await database.create_tables()
    async with database.get_session() as session:
        products_count = await session.scalar(select(func.count(Product.id)))
    if products_count == 0:
        added_count, updated_count = await update_data(database)
        print(f'Добавлено товаров: {added_count}')
    yield
    await database.close()

app = FastAPI(title='Каталог товаров DummyJSON', lifespan=lifespan)

@app.get('/category/{category_name}')
async def get_category_products(category_name:str):
    key = f'category:{category_name.strip().lower()}'
    data = get_cache(key)
    if data is not None:
        return data

    async with database.get_session() as session:
        category = await session.scalar(select(Category).where(func.lower(Category.name) == category_name.strip().lower()))
        if category is None:
            raise HTTPException(status_code=404, detail=f'Категория не найдена: {category_name}')
        return set_cache(key, await select_products(session, Product.category_id == category.id))

@app.get('/brands/')
async def get_brands():
    data = get_cache('brands')
    if data is not None:
        return data

    async with database.get_session() as session:
        brands = (await session.scalars(select(Brand).order_by(Brand.name))).all()
        return set_cache('brands', [brand.to_dict() for brand in brands])

@app.get('/brand/{brand_name}')
async def get_brand_products(brand_name:str):
    key = f'brand:{brand_name.strip().lower()}'
    data = get_cache(key)
    if data is not None:
        return data

    async with database.get_session() as session:
        brand = await session.scalar(select(Brand).where(func.lower(Brand.name) == brand_name.strip().lower()))
        if brand is None:
            raise HTTPException(status_code=404, detail=f'Бренд не найден: {brand_name}')
        return set_cache(key, await select_products(session, Product.brand_id == brand.id))

@app.get('/products/')
async def get_products():
    data = get_cache('products')
    if data is not None:
        return data

    async with database.get_session() as session:
        return set_cache('products', await select_products(session))

@app.post('/update/')
async def update_catalog():
    added_count, updated_count = await update_data(database)
    cache.clear() # данные изменились, сбрасываем кэш
    return {'added_count': added_count, 'updated_count': updated_count}
