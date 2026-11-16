-- Создание таблиц базы данных каталога товаров (SQLite)

CREATE TABLE IF NOT EXISTS brands (
    name VARCHAR(100) NOT NULL, 
    id INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS categories (
    name VARCHAR(100) NOT NULL, 
    id INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS reviewers (
    name VARCHAR(100) NOT NULL, 
    email VARCHAR(100) NOT NULL, 
    id INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (email)
);

CREATE TABLE IF NOT EXISTS products (
    title VARCHAR(255) NOT NULL, 
    description TEXT, 
    price FLOAT NOT NULL, 
    discount_percentage FLOAT, 
    rating FLOAT, 
    stock INTEGER, 
    sku VARCHAR(50), 
    category_id INTEGER NOT NULL, 
    brand_id INTEGER, 
    id INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (sku), 
    FOREIGN KEY(category_id) REFERENCES categories (id), 
    FOREIGN KEY(brand_id) REFERENCES brands (id)
);

CREATE TABLE IF NOT EXISTS reviews (
    rating INTEGER, 
    comment TEXT, 
    date VARCHAR(30), 
    product_id INTEGER NOT NULL, 
    reviewer_id INTEGER NOT NULL, 
    id INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(product_id) REFERENCES products (id), 
    FOREIGN KEY(reviewer_id) REFERENCES reviewers (id)
);
