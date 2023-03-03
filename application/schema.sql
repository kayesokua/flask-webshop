CREATE TABLE IF NOT EXISTS user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  is_admin BOOLEAN DEFAULT FALSE
  );


CREATE TABLE IF NOT EXISTS product (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  admin_id INTEGER NOT NULL,
  name TEXT UNIQUE NOT NULL,
  price DOUBLE NOT NULL,
  stock INTEGER NOT NULL DEFAULT 0,
  description TEXT NOT NULL,
  image TEXT NOT NULL,
  FOREIGN KEY (admin_id) REFERENCES user (id)
  );

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer_id INTEGER NOT NULL,
    shipping_fee DOUBLE NOT NULL,
    grand_total DOUBLE NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    delivery_house_nr VARCHAR(10) NOT NULL,
    delivery_street VARCHAR(50) NOT NULL,
    delivery_additional VARCHAR(255),
    delivery_state VARCHAR(50) NOT NULL,
    delivery_postal VARCHAR(10) NOT NULL,
    delivery_country VARCHAR(2) NOT NULL,
    instructions VARCHAR(255) NULL,
    delivery_status VARCHAR(10) NOT NULL,
    stripe_payment_id VARCHAR(255),
    FOREIGN KEY (buyer_id) REFERENCES user (id)
  );

CREATE TABLE IF NOT EXISTS order_line (
  order_id INTEGER NOT NULL,
  buyer_id INTEGER NOT NULL,
  qty INTEGER NOT NULL,
  qty_total_price DOUBLE NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders (id),
  FOREIGN KEY (buyer_id) REFERENCES user (id)
);

ALTER TABLE user ADD accept_tos BOOLEAN DEFAULT FALSE;
