-- Insert sample users (passwords are 'password123' encoded with BCrypt)
INSERT INTO users (username, email, password, first_name, last_name, role, enabled, created_at, updated_at) VALUES
('admin', 'admin@example.com', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2uheWG/igi.', 'Admin', 'User', 'ADMIN', true, NOW(), NOW()),
('john_doe', 'john@example.com', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2uheWG/igi.', 'John', 'Doe', 'USER', true, NOW(), NOW()),
('jane_smith', 'jane@example.com', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2uheWG/igi.', 'Jane', 'Smith', 'USER', true, NOW(), NOW());

-- Insert sample products
INSERT INTO products (name, description, price, stock_quantity, category, brand, image_url, active, created_at, updated_at) VALUES
('iPhone 14 Pro', 'Latest Apple smartphone with advanced camera system', 999.99, 50, 'Electronics', 'Apple', 'https://example.com/iphone14pro.jpg', true, NOW(), NOW()),
('Samsung Galaxy S23', 'Flagship Android smartphone with excellent display', 899.99, 30, 'Electronics', 'Samsung', 'https://example.com/galaxys23.jpg', true, NOW(), NOW()),
('MacBook Pro 16"', 'Powerful laptop for professionals', 2499.99, 15, 'Electronics', 'Apple', 'https://example.com/macbookpro16.jpg', true, NOW(), NOW()),
('Dell XPS 13', 'Compact and powerful ultrabook', 1299.99, 25, 'Electronics', 'Dell', 'https://example.com/dellxps13.jpg', true, NOW(), NOW()),
('Sony WH-1000XM4', 'Premium noise-canceling headphones', 349.99, 100, 'Electronics', 'Sony', 'https://example.com/sonywh1000xm4.jpg', true, NOW(), NOW()),
('Nike Air Max 270', 'Comfortable running shoes', 149.99, 200, 'Footwear', 'Nike', 'https://example.com/nikeairmax270.jpg', true, NOW(), NOW()),
('Adidas Ultraboost 22', 'High-performance running shoes', 179.99, 150, 'Footwear', 'Adidas', 'https://example.com/adidasultraboost22.jpg', true, NOW(), NOW()),
('Levi''s 501 Jeans', 'Classic straight-fit jeans', 79.99, 300, 'Clothing', 'Levi''s', 'https://example.com/levis501.jpg', true, NOW(), NOW()),
('The North Face Jacket', 'Waterproof outdoor jacket', 199.99, 75, 'Clothing', 'The North Face', 'https://example.com/tnfjacket.jpg', true, NOW(), NOW()),
('Kindle Paperwhite', 'E-reader with high-resolution display', 139.99, 80, 'Electronics', 'Amazon', 'https://example.com/kindlepaperwhite.jpg', true, NOW(), NOW()),
('Instant Pot Duo', '7-in-1 electric pressure cooker', 89.99, 120, 'Home & Kitchen', 'Instant Pot', 'https://example.com/instantpotduo.jpg', true, NOW(), NOW()),
('Dyson V15 Detect', 'Cordless vacuum cleaner with laser detection', 749.99, 40, 'Home & Kitchen', 'Dyson', 'https://example.com/dysonv15.jpg', true, NOW(), NOW()),
('Fitbit Charge 5', 'Advanced fitness tracker', 179.99, 90, 'Electronics', 'Fitbit', 'https://example.com/fitbitcharge5.jpg', true, NOW(), NOW()),
('Yeti Rambler Tumbler', 'Insulated stainless steel tumbler', 34.99, 250, 'Home & Kitchen', 'Yeti', 'https://example.com/yetirambler.jpg', true, NOW(), NOW()),
('Patagonia Fleece Jacket', 'Sustainable outdoor fleece', 129.99, 60, 'Clothing', 'Patagonia', 'https://example.com/patagoniafleece.jpg', true, NOW(), NOW());

-- Insert sample orders
INSERT INTO orders (user_id, status, total_amount, shipping_address, order_date, created_at, updated_at) VALUES
(2, 'DELIVERED', 1349.98, '123 Main St, Anytown, USA 12345', '2024-01-15 10:30:00', '2024-01-15 10:30:00', '2024-01-20 14:45:00'),
(3, 'SHIPPED', 229.98, '456 Oak Ave, Another City, USA 67890', '2024-01-18 14:20:00', '2024-01-18 14:20:00', '2024-01-19 09:15:00'),
(2, 'PENDING', 999.99, '123 Main St, Anytown, USA 12345', '2024-01-20 16:45:00', '2024-01-20 16:45:00', '2024-01-20 16:45:00');

-- Insert sample order items
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price, created_at, updated_at) VALUES
-- Order 1 items
(1, 1, 1, 999.99, 999.99, '2024-01-15 10:30:00', '2024-01-15 10:30:00'),
(1, 5, 1, 349.99, 349.99, '2024-01-15 10:30:00', '2024-01-15 10:30:00'),
-- Order 2 items
(2, 6, 1, 149.99, 149.99, '2024-01-18 14:20:00', '2024-01-18 14:20:00'),
(2, 8, 1, 79.99, 79.99, '2024-01-18 14:20:00', '2024-01-18 14:20:00'),
-- Order 3 items
(3, 1, 1, 999.99, 999.99, '2024-01-20 16:45:00', '2024-01-20 16:45:00');
