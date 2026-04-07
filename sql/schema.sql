CREATE DATABASE IF NOT EXISTS event_management;
USE event_management;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(190) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'vendor', 'user') NOT NULL,
    INDEX ix_users_email (email)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS vendors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE,
    name VARCHAR(120) NOT NULL,
    category ENUM('Catering', 'Florist', 'Decoration', 'Lighting') NOT NULL,
    contact VARCHAR(120) NOT NULL,
    sell_items VARCHAR(500),
    INDEX ix_vendors_category (category),
    CONSTRAINT fk_vendors_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

SET @col_exists := (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'vendors'
      AND COLUMN_NAME = 'sell_items'
);
SET @ddl := IF(@col_exists = 0,
    'ALTER TABLE vendors ADD COLUMN sell_items VARCHAR(500) NULL',
    'SELECT 1'
);
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INT NOT NULL,
    name VARCHAR(120) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    image VARCHAR(300),
    CONSTRAINT ck_products_price CHECK (price >= 0),
    INDEX ix_products_vendor (vendor_id),
    CONSTRAINT fk_products_vendor FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    CONSTRAINT ck_cart_qty CHECK (quantity > 0),
    UNIQUE KEY uq_cart_user_product (user_id, product_id),
    INDEX ix_cart_user (user_id),
    CONSTRAINT fk_cart_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_cart_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    customer_name VARCHAR(120) NOT NULL,
    customer_number VARCHAR(25) NOT NULL,
    customer_email VARCHAR(190) NOT NULL,
    customer_address VARCHAR(220) NOT NULL,
    customer_state VARCHAR(120) NOT NULL,
    customer_city VARCHAR(120) NOT NULL,
    customer_pincode VARCHAR(20) NOT NULL,
    status ENUM('Received', 'Ready for Shipping', 'Out for Delivery') NOT NULL DEFAULT 'Received',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_orders_total CHECK (total >= 0),
    INDEX ix_orders_user (user_id),
    INDEX ix_orders_status (status),
    CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    CONSTRAINT ck_order_items_qty CHECK (quantity > 0),
    INDEX ix_order_items_order (order_id),
    CONSTRAINT fk_order_items_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    CONSTRAINT fk_order_items_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS membership (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    duration ENUM('6 months', '1 year', '2 years') NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    INDEX ix_membership_user (user_id),
    CONSTRAINT fk_membership_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL UNIQUE,
    payment_method ENUM('Cash', 'UPI') NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Completed',
    INDEX ix_transactions_order (order_id),
    CONSTRAINT fk_transactions_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS guest_list (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(190),
    address VARCHAR(200),
    INDEX ix_guest_user (user_id),
    CONSTRAINT fk_guest_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS product_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INT NOT NULL,
    requested_by INT NOT NULL,
    item_name VARCHAR(120) NOT NULL,
    note VARCHAR(300),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX ix_requests_vendor (vendor_id),
    CONSTRAINT fk_requests_vendor FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE,
    CONSTRAINT fk_requests_user FOREIGN KEY (requested_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;
