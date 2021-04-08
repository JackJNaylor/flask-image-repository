DROP TABLE IF EXISTS users;

CREATE TABLE users (
    userId INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL
);

DROP TABLE IF EXISTS images;

CREATE TABLE images (
    imageId INTEGER PRIMARY KEY AUTOINCREMENT,
    imageName TEXT NOT NULL,
    unitPrice INTEGER NOT NULL,
    discount INTEGER DEFAULT 0,
    inventory INTEGER NOT NULL,
    description TEXT,
    data BLOB,
    userId INTEGER NOT NULL,
    FOREIGN KEY(userId) REFERENCES users(userId)
);

DROP TABLE IF EXISTS orders;

CREATE TABLE orders (
    orderId INTEGER PRIMARY KEY AUTOINCREMENT,
    dateOrdered NOT NULL DEFAULT CURRENT_DATE,
    status TEXT NOT NULL DEFAULT 'ORDER RECEIVED',
    quantity TEXT NOT NULL,
    orderTotal TEXT NOT NULL,
    imageId INTEGER NOT NULL,
    buyerId TEXT NOT NULL,
    sellerId TEXT NOT NULL,
    FOREIGN KEY (imageId) REFERENCES images(imageId),
    FOREIGN KEY (buyerId) REFERENCES users(userId),
    FOREIGN KEY (sellerId) REFERENCES users(userId)
);