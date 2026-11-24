-- MySQL Database Setup for E-commerce Chatbot
-- Olist E-commerce Database Schema

DROP DATABASE IF EXISTS ecommerce_olist;
CREATE DATABASE ecommerce_olist CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ecommerce_olist;

-- Customers table
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_unique_id VARCHAR(50),
    customer_zip_code_prefix VARCHAR(10),
    customer_city VARCHAR(100),
    customer_state VARCHAR(2)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Geolocation table
CREATE TABLE geolocation (
    geolocation_id INT AUTO_INCREMENT PRIMARY KEY,
    geolocation_zip_code_prefix VARCHAR(10),
    geolocation_lat DECIMAL(10, 8),
    geolocation_lng DECIMAL(11, 8),
    geolocation_city VARCHAR(100),
    geolocation_state VARCHAR(2),
    INDEX idx_zip (geolocation_zip_code_prefix)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Sellers table
CREATE TABLE sellers (
    seller_id VARCHAR(50) PRIMARY KEY,
    seller_zip_code_prefix VARCHAR(10),
    seller_city VARCHAR(100),
    seller_state VARCHAR(2)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Product category translation table
CREATE TABLE product_category_name_translation (
    product_category_name VARCHAR(100) PRIMARY KEY,
    product_category_name_english VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Products table
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_category_name VARCHAR(100),
    product_name_length INT,
    product_description_length INT,
    product_photos_qty INT,
    product_weight_g INT,
    product_length_cm INT,
    product_height_cm INT,
    product_width_cm INT,
    FOREIGN KEY (product_category_name) REFERENCES product_category_name_translation(product_category_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Orders table
CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    order_status VARCHAR(20),
    order_purchase_timestamp DATETIME,
    order_approved_at DATETIME,
    order_delivered_carrier_date DATETIME,
    order_delivered_customer_date DATETIME,
    order_estimated_delivery_date DATETIME,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    INDEX idx_status (order_status),
    INDEX idx_purchase_date (order_purchase_timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Order items table
CREATE TABLE order_items (
    order_id VARCHAR(50),
    order_item_id INT,
    product_id VARCHAR(50),
    seller_id VARCHAR(50),
    shipping_limit_date DATETIME,
    price DECIMAL(10, 2),
    freight_value DECIMAL(10, 2),
    PRIMARY KEY (order_id, order_item_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id),
    INDEX idx_product (product_id),
    INDEX idx_seller (seller_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Order payments table
CREATE TABLE order_payments (
    order_id VARCHAR(50),
    payment_sequential INT,
    payment_type VARCHAR(20),
    payment_installments INT,
    payment_value DECIMAL(10, 2),
    PRIMARY KEY (order_id, payment_sequential),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    INDEX idx_payment_type (payment_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Order reviews table
CREATE TABLE order_reviews (
    review_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50),
    review_score INT,
    review_comment_title VARCHAR(255),
    review_comment_message TEXT,
    review_creation_date DATETIME,
    review_answer_timestamp DATETIME,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    INDEX idx_score (review_score),
    INDEX idx_creation_date (review_creation_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Leads qualified table (marketing leads)
CREATE TABLE leads_qualified (
    mql_id VARCHAR(50) PRIMARY KEY,
    first_contact_date DATETIME,
    landing_page_id VARCHAR(50),
    origin VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Leads closed table (closed deals)
CREATE TABLE leads_closed (
    mql_id VARCHAR(50) PRIMARY KEY,
    seller_id VARCHAR(50),
    sdr_id VARCHAR(50),
    sr_id VARCHAR(50),
    won_date DATETIME,
    business_segment VARCHAR(100),
    lead_type VARCHAR(50),
    lead_behaviour_profile VARCHAR(50),
    has_company BOOLEAN,
    has_gtin BOOLEAN,
    average_stock VARCHAR(50),
    business_type VARCHAR(50),
    declared_product_catalog_size INT,
    declared_monthly_revenue DECIMAL(10, 2),
    FOREIGN KEY (mql_id) REFERENCES leads_qualified(mql_id),
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert sample data for product categories
INSERT INTO product_category_name_translation VALUES
('beleza_saude', 'health_beauty'),
('informatica_acessorios', 'computers_accessories'),
('automotivo', 'auto'),
('cama_mesa_banho', 'bed_bath_table'),
('moveis_decoracao', 'furniture_decor'),
('esporte_lazer', 'sports_leisure'),
('perfumaria', 'perfumery'),
('utilidades_domesticas', 'housewares'),
('ferramentas_jardim', 'garden_tools'),
('telefonia', 'telephony'),
('relogios_presentes', 'watches_gifts'),
('brinquedos', 'toys'),
('livros_tecnicos', 'books_technical'),
('eletronicos', 'electronics'),
('casa_construcao', 'home_construction');

-- Insert sample customers
INSERT INTO customers VALUES
('cust001', 'unique001', '01310', 'sao paulo', 'SP'),
('cust002', 'unique002', '02140', 'rio de janeiro', 'RJ'),
('cust003', 'unique003', '30130', 'belo horizonte', 'MG'),
('cust004', 'unique004', '80010', 'curitiba', 'PR'),
('cust005', 'unique005', '90010', 'porto alegre', 'RS'),
('cust006', 'unique006', '40010', 'salvador', 'BA'),
('cust007', 'unique007', '50010', 'recife', 'PE'),
('cust008', 'unique008', '70040', 'brasilia', 'DF'),
('cust009', 'unique009', '60010', 'fortaleza', 'CE'),
('cust010', 'unique010', '66010', 'belem', 'PA');

-- Insert sample sellers
INSERT INTO sellers VALUES
('seller001', '01310', 'sao paulo', 'SP'),
('seller002', '02140', 'rio de janeiro', 'RJ'),
('seller003', '30130', 'belo horizonte', 'MG'),
('seller004', '80010', 'curitiba', 'PR'),
('seller005', '90010', 'porto alegre', 'RS');

-- Insert sample products
INSERT INTO products VALUES
('prod001', 'beleza_saude', 50, 500, 3, 500, 15, 10, 10),
('prod002', 'informatica_acessorios', 60, 800, 5, 1200, 25, 20, 15),
('prod003', 'automotivo', 45, 400, 2, 800, 20, 15, 12),
('prod004', 'moveis_decoracao', 70, 1000, 8, 5000, 100, 80, 60),
('prod005', 'esporte_lazer', 55, 600, 4, 1500, 30, 25, 20),
('prod006', 'eletronicos', 65, 900, 6, 2000, 35, 30, 25),
('prod007', 'brinquedos', 40, 300, 3, 400, 20, 15, 15),
('prod008', 'livros_tecnicos', 75, 1200, 1, 600, 25, 3, 20),
('prod009', 'telefonia', 58, 700, 4, 300, 15, 8, 7),
('prod010', 'relogios_presentes', 48, 450, 3, 200, 10, 5, 8);

-- Insert sample orders
INSERT INTO orders VALUES
('order001', 'cust001', 'delivered', '2024-01-15 10:30:00', '2024-01-15 11:00:00', '2024-01-16 09:00:00', '2024-01-18 14:30:00', '2024-01-20 23:59:59'),
('order002', 'cust002', 'delivered', '2024-01-16 14:20:00', '2024-01-16 15:00:00', '2024-01-17 10:00:00', '2024-01-19 16:45:00', '2024-01-22 23:59:59'),
('order003', 'cust003', 'shipped', '2024-01-18 09:15:00', '2024-01-18 10:00:00', '2024-01-19 08:30:00', NULL, '2024-01-23 23:59:59'),
('order004', 'cust001', 'delivered', '2024-01-20 16:40:00', '2024-01-20 17:00:00', '2024-01-21 11:00:00', '2024-01-23 13:20:00', '2024-01-25 23:59:59'),
('order005', 'cust004', 'processing', '2024-01-22 11:30:00', '2024-01-22 12:00:00', NULL, NULL, '2024-01-27 23:59:59'),
('order006', 'cust005', 'delivered', '2024-01-23 13:50:00', '2024-01-23 14:30:00', '2024-01-24 09:00:00', '2024-01-26 15:10:00', '2024-01-28 23:59:59'),
('order007', 'cust002', 'delivered', '2024-01-24 10:20:00', '2024-01-24 11:00:00', '2024-01-25 08:30:00', '2024-01-27 11:40:00', '2024-01-29 23:59:59'),
('order008', 'cust006', 'canceled', '2024-01-25 15:30:00', NULL, NULL, NULL, '2024-01-30 23:59:59'),
('order009', 'cust007', 'delivered', '2024-01-26 12:15:00', '2024-01-26 13:00:00', '2024-01-27 10:00:00', '2024-01-29 14:25:00', '2024-01-31 23:59:59'),
('order010', 'cust003', 'delivered', '2024-01-27 14:45:00', '2024-01-27 15:30:00', '2024-01-28 09:00:00', '2024-01-30 16:30:00', '2024-02-01 23:59:59');

-- Insert sample order items
INSERT INTO order_items VALUES
('order001', 1, 'prod001', 'seller001', '2024-01-16 23:59:59', 129.90, 15.50),
('order002', 1, 'prod002', 'seller002', '2024-01-17 23:59:59', 599.00, 25.00),
('order003', 1, 'prod003', 'seller003', '2024-01-19 23:59:59', 249.90, 18.75),
('order004', 1, 'prod005', 'seller001', '2024-01-21 23:59:59', 189.90, 22.00),
('order004', 2, 'prod007', 'seller002', '2024-01-21 23:59:59', 79.90, 12.50),
('order005', 1, 'prod006', 'seller004', '2024-01-23 23:59:59', 1299.00, 35.00),
('order006', 1, 'prod004', 'seller005', '2024-01-24 23:59:59', 899.00, 80.00),
('order007', 1, 'prod008', 'seller002', '2024-01-25 23:59:59', 89.90, 10.00),
('order009', 1, 'prod009', 'seller001', '2024-01-27 23:59:59', 499.00, 20.00),
('order010', 1, 'prod010', 'seller003', '2024-01-28 23:59:59', 299.90, 15.00);

-- Insert sample payments
INSERT INTO order_payments VALUES
('order001', 1, 'credit_card', 3, 145.40),
('order002', 1, 'credit_card', 2, 624.00),
('order003', 1, 'boleto', 1, 268.65),
('order004', 1, 'credit_card', 1, 292.80),
('order005', 1, 'credit_card', 12, 1334.00),
('order006', 1, 'credit_card', 6, 979.00),
('order007', 1, 'debit_card', 1, 99.90),
('order009', 1, 'credit_card', 2, 519.00),
('order010', 1, 'boleto', 1, 314.90);

-- Insert sample reviews
INSERT INTO order_reviews VALUES
('review001', 'order001', 5, 'Excelente!', 'Produto chegou rapidinho e bem embalado.', '2024-01-19 10:00:00', '2024-01-19 14:00:00'),
('review002', 'order002', 4, 'Bom produto', 'Qualidade boa, entrega dentro do prazo.', '2024-01-20 15:30:00', '2024-01-20 18:00:00'),
('review003', 'order004', 5, 'Perfeito', 'Adorei a compra, recomendo!', '2024-01-24 11:20:00', '2024-01-24 16:00:00'),
('review004', 'order006', 3, 'Regular', 'Produto ok, mas entrega atrasou um pouco.', '2024-01-27 13:45:00', '2024-01-27 17:30:00'),
('review005', 'order007', 5, 'Muito bom', 'Exatamente como descrito.', '2024-01-28 09:15:00', '2024-01-28 12:00:00'),
('review006', 'order009', 4, 'Recomendo', 'Boa experiência de compra.', '2024-01-30 14:30:00', '2024-01-30 18:00:00'),
('review007', 'order010', 5, 'Ótimo', 'Produto de qualidade!', '2024-01-31 16:00:00', '2024-02-01 10:00:00');

-- Create some useful views for analysis
CREATE VIEW order_summary AS
SELECT 
    o.order_id,
    o.customer_id,
    o.order_status,
    o.order_purchase_timestamp,
    COUNT(oi.order_item_id) as total_items,
    SUM(oi.price + oi.freight_value) as total_value,
    AVG(r.review_score) as avg_review_score
FROM orders o
LEFT JOIN order_items oi ON o.order_id = oi.order_id
LEFT JOIN order_reviews r ON o.order_id = r.order_id
GROUP BY o.order_id, o.customer_id, o.order_status, o.order_purchase_timestamp;

CREATE VIEW product_performance AS
SELECT 
    p.product_id,
    p.product_category_name,
    t.product_category_name_english,
    COUNT(oi.order_id) as total_orders,
    SUM(oi.price) as total_revenue,
    AVG(oi.price) as avg_price
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN product_category_name_translation t ON p.product_category_name = t.product_category_name
GROUP BY p.product_id, p.product_category_name, t.product_category_name_english;

SHOW TABLES;

SELECT 'Database ecommerce_olist created successfully!' as Status;
