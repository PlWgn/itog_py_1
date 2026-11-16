from sqlalchemy import select
from models import Category, Brand, Product, Reviewer, Review
from loader import Loader

async def save_data(session, data:dict):
    categories = {category.name: category for category in (await session.scalars(select(Category))).all()}
    brands = {brand.name: brand for brand in (await session.scalars(select(Brand))).all()}
    reviewers = {reviewer.email: reviewer for reviewer in (await session.scalars(select(Reviewer))).all()}
    added_count = 0
    updated_count = 0

    for category_name in data:
        if category_name not in categories:
            categories[category_name] = Category({'name': category_name})
            session.add(categories[category_name])

        for item in data[category_name]:
            brand = None
            brand_name = item.get('brand')
            if brand_name:
                if brand_name not in brands:
                    brands[brand_name] = Brand({'name': brand_name})
                    session.add(brands[brand_name])
                brand = brands[brand_name]

            values = {
                'id': item.get('id'),
                'title': item.get('title', 'Без названия'),
                'description': item.get('description'),
                'price': item.get('price', 0),
                'discount_percentage': item.get('discountPercentage'),
                'rating': item.get('rating'),
                'stock': item.get('stock'),
                'sku': item.get('sku')
            }

            product = await session.get(Product, item.get('id'))

            # товар уже есть в базе, обновляем его данные
            if product is not None:
                for key in values:
                    setattr(product, key, values[key])
                product.category = categories[category_name]
                product.brand = brand
                updated_count += 1
                continue

            product = Product(values)
            product.category = categories[category_name]
            product.brand = brand

            for item_review in item.get('reviews', []):
                email = item_review.get('reviewerEmail')
                if not email:
                    continue
                if email not in reviewers:
                    reviewers[email] = Reviewer({'name': item_review.get('reviewerName', 'Неизвестный'), 'email': email})
                    session.add(reviewers[email])

                review = Review({
                    'rating': item_review.get('rating'),
                    'comment': item_review.get('comment'),
                    'date': item_review.get('date')
                })
                review.reviewer = reviewers[email]
                product.reviews.append(review)

            session.add(product)
            added_count += 1

    await session.commit()
    return (added_count, updated_count)

async def update_data(database, categories:list = None):
    await database.create_tables()

    loader = Loader()
    data = await loader.download(categories)

    async with database.get_session() as session:
        return await save_data(session, data)
