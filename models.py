try:
    from sqlalchemy import Column, Integer, Float, String, Text, ForeignKey
    from sqlalchemy.orm import DeclarativeBase, relationship
except ImportError:
    print('Не установлена библиотека sqlalchemy. Чтобы установить используйте pip3 install -U sqlalchemy greenlet aiosqlite')
    raise SystemExit

class Base(DeclarativeBase):
    pass

class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)

    def __init__(self, data:dict):
        columns = self.__table__.columns.keys()
        for key, value in data.items():
            if key in columns:
                setattr(self, key, value)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.to_dict()})'

    def to_dict(self):
        return {column: getattr(self, column) for column in self.__table__.columns.keys()}

class Category(BaseModel):
    __tablename__ = 'categories'

    name = Column(String(100), unique=True, nullable=False)

    products = relationship('Product', back_populates='category')

class Brand(BaseModel):
    __tablename__ = 'brands'

    name = Column(String(100), unique=True, nullable=False)

    products = relationship('Product', back_populates='brand')

class Product(BaseModel):
    __tablename__ = 'products'

    title = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    discount_percentage = Column(Float)
    rating = Column(Float)
    stock = Column(Integer)
    sku = Column(String(50), unique=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    brand_id = Column(Integer, ForeignKey('brands.id')) # у части товаров в DummyJSON нет бренда

    category = relationship('Category', back_populates='products')
    brand = relationship('Brand', back_populates='products')
    reviews = relationship('Review', back_populates='product', cascade='all, delete-orphan')

# имя автора зависит от email, а не от отзыва, поэтому авторы вынесены в отдельную таблицу (3NF)
class Reviewer(BaseModel):
    __tablename__ = 'reviewers'

    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)

    reviews = relationship('Review', back_populates='reviewer')

class Review(BaseModel):
    __tablename__ = 'reviews'

    rating = Column(Integer)
    comment = Column(Text)
    date = Column(String(30))
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    reviewer_id = Column(Integer, ForeignKey('reviewers.id'), nullable=False)

    product = relationship('Product', back_populates='reviews')
    reviewer = relationship('Reviewer', back_populates='reviews')
