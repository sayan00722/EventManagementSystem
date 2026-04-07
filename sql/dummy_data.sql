USE event_management;

-- Shared bcrypt hash for password: Admin@123
SET @pwd_hash = '$2b$12$15is9nQx2kNhBBX6YsJhEe9N6byjHgNsx3Rp3XIanFkFJxuxMxDPW';

INSERT INTO users (name, email, password, role) VALUES
('BloomNest Florist', 'florist1@event.com', @pwd_hash, 'vendor'),
('Royal Petal Studio', 'florist2@event.com', @pwd_hash, 'vendor'),
('Crown Caterers', 'catering1@event.com', @pwd_hash, 'vendor'),
('Urban Feast Co', 'catering2@event.com', @pwd_hash, 'vendor'),
('Luxe Decor Lab', 'decor1@event.com', @pwd_hash, 'vendor'),
('Glowline Lights', 'lighting1@event.com', @pwd_hash, 'vendor'),
('Demo User 2', 'user2@event.com', @pwd_hash, 'user'),
('Demo User 3', 'user3@event.com', @pwd_hash, 'user'),
('Demo User 4', 'user4@event.com', @pwd_hash, 'user'),
('Demo User 5', 'user5@event.com', @pwd_hash, 'user'),
('Demo User 6', 'user6@event.com', @pwd_hash, 'user')
ON DUPLICATE KEY UPDATE name = VALUES(name);

INSERT INTO vendors (user_id, name, category, contact, sell_items)
SELECT id, 'BloomNest Florist', 'Florist', '9000000011', 'Bouquets, Bridal Posy, Stage Garland'
FROM users WHERE email = 'florist1@event.com'
ON DUPLICATE KEY UPDATE contact = VALUES(contact), sell_items = VALUES(sell_items);

INSERT INTO vendors (user_id, name, category, contact, sell_items)
SELECT id, 'Royal Petal Studio', 'Florist', '9000000012', 'Premium Roses, Table Flowers, Orchid Wall'
FROM users WHERE email = 'florist2@event.com'
ON DUPLICATE KEY UPDATE contact = VALUES(contact), sell_items = VALUES(sell_items);

INSERT INTO vendors (user_id, name, category, contact, sell_items)
SELECT id, 'Crown Caterers', 'Catering', '9000000013', 'Buffet, Live Counter, Dessert Bar'
FROM users WHERE email = 'catering1@event.com'
ON DUPLICATE KEY UPDATE contact = VALUES(contact), sell_items = VALUES(sell_items);

INSERT INTO vendors (user_id, name, category, contact, sell_items)
SELECT id, 'Urban Feast Co', 'Catering', '9000000014', 'Plated Dinner, Mocktails, Snacks'
FROM users WHERE email = 'catering2@event.com'
ON DUPLICATE KEY UPDATE contact = VALUES(contact), sell_items = VALUES(sell_items);

INSERT INTO vendors (user_id, name, category, contact, sell_items)
SELECT id, 'Luxe Decor Lab', 'Decoration', '9000000015', 'Stage Decor, Entrance Arch, Table Decor'
FROM users WHERE email = 'decor1@event.com'
ON DUPLICATE KEY UPDATE contact = VALUES(contact), sell_items = VALUES(sell_items);

INSERT INTO vendors (user_id, name, category, contact, sell_items)
SELECT id, 'Glowline Lights', 'Lighting', '9000000016', 'Fairy Lights, LED Wash, Spot Lights'
FROM users WHERE email = 'lighting1@event.com'
ON DUPLICATE KEY UPDATE contact = VALUES(contact), sell_items = VALUES(sell_items);

-- BloomNest Florist products (6)
INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'Rose Bouquet Classic', 1200.00, 'https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg'
FROM vendors v WHERE v.name = 'BloomNest Florist';
INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'Lily Basket', 1500.00, 'https://images.pexels.com/photos/161154/still-life-flower-pot-floral-161154.jpeg'
FROM vendors v WHERE v.name = 'BloomNest Florist';
INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'Aisle Flower Line', 2500.00, 'https://images.pexels.com/photos/169190/pexels-photo-169190.jpeg'
FROM vendors v WHERE v.name = 'BloomNest Florist';
INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'Floral Welcome Board', 1800.00, 'https://images.pexels.com/photos/1005417/pexels-photo-1005417.jpeg'
FROM vendors v WHERE v.name = 'BloomNest Florist';
INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'Bridal Posy', 2200.00, 'https://images.pexels.com/photos/2959192/pexels-photo-2959192.jpeg'
FROM vendors v WHERE v.name = 'BloomNest Florist';
INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'Centerpiece Combo', 2800.00, 'https://images.pexels.com/photos/949587/pexels-photo-949587.jpeg'
FROM vendors v WHERE v.name = 'BloomNest Florist';

-- Crown Caterers products (6)
INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'North Indian Buffet', 12000.00, 'https://images.pexels.com/photos/958545/pexels-photo-958545.jpeg'
FROM vendors v WHERE v.name = 'Crown Caterers';
INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'South Indian Combo', 10000.00, 'https://images.pexels.com/photos/723198/pexels-photo-723198.jpeg'
FROM vendors v WHERE v.name = 'Crown Caterers';
INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'Live Pasta Counter', 8500.00, 'https://images.pexels.com/photos/1437267/pexels-photo-1437267.jpeg'
FROM vendors v WHERE v.name = 'Crown Caterers';
INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'Street Food Station', 7800.00, 'https://images.pexels.com/photos/70497/pexels-photo-70497.jpeg'
FROM vendors v WHERE v.name = 'Crown Caterers';
INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'Dessert Bar Premium', 9200.00, 'https://images.pexels.com/photos/3026808/pexels-photo-3026808.jpeg'
FROM vendors v WHERE v.name = 'Crown Caterers';
INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'Mocktail Setup', 6400.00, 'https://images.pexels.com/photos/302899/pexels-photo-302899.jpeg'
FROM vendors v WHERE v.name = 'Crown Caterers';

-- Luxe Decor Lab products (6)
INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'Grand Stage Theme', 24000.00, 'https://images.pexels.com/photos/587741/pexels-photo-587741.jpeg'
FROM vendors v WHERE v.name = 'Luxe Decor Lab';
INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'Pastel Backdrop', 15000.00, 'https://images.pexels.com/photos/1405937/pexels-photo-1405937.jpeg'
FROM vendors v WHERE v.name = 'Luxe Decor Lab';
INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'Entrance Floral Arch', 13500.00, 'https://images.pexels.com/photos/265801/pexels-photo-265801.jpeg'
FROM vendors v WHERE v.name = 'Luxe Decor Lab';
INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'Table Styling Kit', 7600.00, 'https://images.pexels.com/photos/587741/pexels-photo-587741.jpeg'
FROM vendors v WHERE v.name = 'Luxe Decor Lab';
INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'Minimal Mandap', 18000.00, 'https://images.pexels.com/photos/1024993/pexels-photo-1024993.jpeg'
FROM vendors v WHERE v.name = 'Luxe Decor Lab';
INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'Photo Booth Corner', 9200.00, 'https://images.pexels.com/photos/169198/pexels-photo-169198.jpeg'
FROM vendors v WHERE v.name = 'Luxe Decor Lab';

-- Glowline Lights products (6)
INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'Fairy Light Curtain', 5200.00, 'https://images.pexels.com/photos/1190298/pexels-photo-1190298.jpeg'
FROM vendors v WHERE v.name = 'Glowline Lights';
INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'Warm LED Wash', 6800.00, 'https://images.pexels.com/photos/2747449/pexels-photo-2747449.jpeg'
FROM vendors v WHERE v.name = 'Glowline Lights';
INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'Stage Spot Package', 7900.00, 'https://images.pexels.com/photos/1105666/pexels-photo-1105666.jpeg'
FROM vendors v WHERE v.name = 'Glowline Lights';
INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'Garden Ambient Lights', 7300.00, 'https://images.pexels.com/photos/1779487/pexels-photo-1779487.jpeg'
FROM vendors v WHERE v.name = 'Glowline Lights';
INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'Ceiling Pixel Glow', 8700.00, 'https://images.pexels.com/photos/167092/pexels-photo-167092.jpeg'
FROM vendors v WHERE v.name = 'Glowline Lights';
INSERT INTO products (vendor_id, name, price, image)
SELECT v.id, 'Pathway Light String', 4500.00, 'https://images.pexels.com/photos/577585/pexels-photo-577585.jpeg'
FROM vendors v WHERE v.name = 'Glowline Lights';
