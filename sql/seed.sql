USE event_management;

INSERT INTO users (name, email, password, role)
VALUES
('Admin', 'admin@event.com', '$2b$12$15is9nQx2kNhBBX6YsJhEe9N6byjHgNsx3Rp3XIanFkFJxuxMxDPW', 'admin'),
('Vendor A', 'vendor@event.com', '$2b$12$15is9nQx2kNhBBX6YsJhEe9N6byjHgNsx3Rp3XIanFkFJxuxMxDPW', 'vendor'),
('User A', 'user@event.com', '$2b$12$15is9nQx2kNhBBX6YsJhEe9N6byjHgNsx3Rp3XIanFkFJxuxMxDPW', 'user')
ON DUPLICATE KEY UPDATE name = VALUES(name);

INSERT INTO vendors (user_id, name, category, contact, sell_items)
SELECT id, 'Vendor A', 'Catering', '9876543210', 'Buffet, Live Counter, Dessert Bar'
FROM users
WHERE email = 'vendor@event.com'
ON DUPLICATE KEY UPDATE name = VALUES(name);

INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'Wedding Package', 100.00, 'https://example.com/package.png'
FROM vendors v
WHERE v.name = 'Vendor A'
LIMIT 1;
