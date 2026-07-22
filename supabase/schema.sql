-- Maré Clara · schema + dados demo para Supabase (PostgreSQL)
-- Cole este arquivo em: Supabase → SQL Editor → New query → Run

BEGIN;

DROP TABLE IF EXISTS stock_movements CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS reservations CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS tents CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  username VARCHAR(80) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(20) NOT NULL,
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tents (
  id SERIAL PRIMARY KEY,
  number INTEGER NOT NULL UNIQUE,
  zone VARCHAR(40) DEFAULT 'Areia',
  capacity INTEGER DEFAULT 4,
  daily_price DOUBLE PRECISION DEFAULT 80,
  status VARCHAR(20) DEFAULT 'livre',
  notes VARCHAR(255) DEFAULT ''
);

CREATE TABLE reservations (
  id SERIAL PRIMARY KEY,
  tent_id INTEGER NOT NULL REFERENCES tents(id),
  customer_name VARCHAR(120) NOT NULL,
  customer_phone VARCHAR(40) DEFAULT '',
  date DATE NOT NULL,
  time_slot VARCHAR(20) DEFAULT 'dia todo',
  value DOUBLE PRECISION DEFAULT 0,
  status VARCHAR(20) DEFAULT 'confirmada',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE sessions (
  id SERIAL PRIMARY KEY,
  tent_id INTEGER NOT NULL REFERENCES tents(id),
  reservation_id INTEGER REFERENCES reservations(id),
  customer_name VARCHAR(120) DEFAULT 'Cliente',
  customer_phone VARCHAR(40) DEFAULT '',
  opened_at TIMESTAMP DEFAULT NOW(),
  closed_at TIMESTAMP,
  status VARCHAR(30) DEFAULT 'aberta',
  rental_charged BOOLEAN DEFAULT FALSE
);

CREATE TABLE categories (
  id SERIAL PRIMARY KEY,
  name VARCHAR(80) NOT NULL UNIQUE,
  sector VARCHAR(20) DEFAULT 'cozinha',
  sort_order INTEGER DEFAULT 0
);

CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  category_id INTEGER NOT NULL REFERENCES categories(id),
  name VARCHAR(120) NOT NULL,
  description VARCHAR(255) DEFAULT '',
  price DOUBLE PRECISION NOT NULL,
  available BOOLEAN DEFAULT TRUE,
  stock_qty INTEGER DEFAULT 0,
  stock_min INTEGER DEFAULT 5,
  kind VARCHAR(20) DEFAULT 'produto',
  image_url VARCHAR(500) DEFAULT ''
);

CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  session_id INTEGER NOT NULL REFERENCES sessions(id),
  created_at TIMESTAMP DEFAULT NOW(),
  notes VARCHAR(255) DEFAULT '',
  status VARCHAR(20) DEFAULT 'recebido',
  source VARCHAR(20) DEFAULT 'cliente',
  payment_mode VARCHAR(20) DEFAULT 'na_conta',
  payment_status VARCHAR(20) DEFAULT 'pendente',
  payment_method VARCHAR(20) DEFAULT ''
);

CREATE TABLE order_items (
  id SERIAL PRIMARY KEY,
  order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  product_id INTEGER NOT NULL REFERENCES products(id),
  product_name VARCHAR(120) NOT NULL,
  unit_price DOUBLE PRECISION NOT NULL,
  quantity INTEGER DEFAULT 1,
  notes VARCHAR(255) DEFAULT '',
  status VARCHAR(20) DEFAULT 'recebido',
  sector VARCHAR(20) DEFAULT 'cozinha'
);

CREATE TABLE payments (
  id SERIAL PRIMARY KEY,
  session_id INTEGER NOT NULL REFERENCES sessions(id),
  order_id INTEGER REFERENCES orders(id),
  method VARCHAR(20) NOT NULL,
  amount DOUBLE PRECISION NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  notes VARCHAR(255) DEFAULT ''
);

CREATE TABLE stock_movements (
  id SERIAL PRIMARY KEY,
  product_id INTEGER NOT NULL REFERENCES products(id),
  quantity INTEGER NOT NULL,
  reason VARCHAR(120) DEFAULT '',
  created_at TIMESTAMP DEFAULT NOW(),
  user_id INTEGER REFERENCES users(id)
);

-- App Flask acessa via connection string (role postgres), não via anon key.
-- Desativa RLS para o trabalho acadêmico (acesso server-side).
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE tents DISABLE ROW LEVEL SECURITY;
ALTER TABLE reservations DISABLE ROW LEVEL SECURITY;
ALTER TABLE sessions DISABLE ROW LEVEL SECURITY;
ALTER TABLE categories DISABLE ROW LEVEL SECURITY;
ALTER TABLE products DISABLE ROW LEVEL SECURITY;
ALTER TABLE orders DISABLE ROW LEVEL SECURITY;
ALTER TABLE order_items DISABLE ROW LEVEL SECURITY;
ALTER TABLE payments DISABLE ROW LEVEL SECURITY;
ALTER TABLE stock_movements DISABLE ROW LEVEL SECURITY;

INSERT INTO users (name, username, password_hash, role, active) VALUES
('Lojista Demo', 'admin', 'scrypt:32768:8:1$mr8klFvYhhQNZgUm$2a3bb7046a94c1030bbbf2aceb6bc91bec1e5d0a1ebf5c6e827b6f2956c32cad2f7a618c4ac1fd2f67f651752d103071a7a913d681195531f5f1be46dbc71a5b', 'lojista', TRUE),
('Garçom Demo', 'garcom', 'scrypt:32768:8:1$NMANL4ziKREvB1ey$5dea5ded1f1c45f3c3b33cca9045b2433d7be8126ae816a8387d4fe3fe74f311efb9f00b814ad330a132a90e0bd0394e71341419f92ced24c2c10c101998bf5c', 'garcom', TRUE);

-- Tendas 1..20
INSERT INTO tents (number, zone, capacity, daily_price, status)
SELECT
  n,
  (ARRAY['Frente Mar', 'Meio', 'Fundo'])[((n - 1) % 3) + 1],
  CASE WHEN n % 2 = 0 THEN 4 ELSE 2 END,
  CASE WHEN n <= 8 THEN 100 ELSE 80 END,
  CASE WHEN n = 5 THEN 'reservada' ELSE 'livre' END
FROM generate_series(1, 20) AS n;

INSERT INTO categories (name, sector, sort_order) VALUES
('Bebidas', 'bar', 1),
('Porções', 'cozinha', 2),
('Lanches', 'cozinha', 3),
('Sobremesas', 'cozinha', 4),
('Serviços', 'servico', 5);

INSERT INTO products (category_id, name, description, price, stock_qty, stock_min, kind, image_url) VALUES
(1, 'Água Mineral 500ml', 'Gelada, sem gás', 5, 120, 20, 'produto', '/static/img/products/agua.jpg'),
(1, 'Cerveja Lata', '300ml bem gelada', 9, 200, 40, 'produto', '/static/img/products/cerveja.jpg'),
(1, 'Caipirinha', 'Limão, gelo e cachaça', 18, 80, 10, 'produto', '/static/img/products/caipi.jpg'),
(1, 'Suco Natural', 'Laranja ou maracujá', 12, 50, 10, 'produto', '/static/img/products/suco.jpg'),
(1, 'Água de Coco', 'Natural, gelada', 10, 60, 15, 'produto', '/static/img/products/coco.jpg'),
(1, 'Refrigerante Lata', 'Diversos sabores', 8, 100, 20, 'produto', '/static/img/products/refri.jpg'),
(2, 'Batata Frita', 'Porção grande crocante', 28, 40, 8, 'produto', '/static/img/products/batata.jpg'),
(2, 'Isca de Peixe', 'Com molho tártaro', 42, 30, 5, 'produto', '/static/img/products/peixe.jpg'),
(2, 'Camarão Empanado', '400g servidos quentes', 55, 25, 5, 'produto', '/static/img/products/camarao.jpg'),
(2, 'Pastel de Feira', 'Carne ou queijo (6 un)', 25, 35, 8, 'produto', '/static/img/products/pastel.jpg'),
(3, 'X-Burger Praia', 'Blend 160g, queijo e salada', 32, 40, 8, 'produto', '/static/img/products/burger.jpg'),
(3, 'Hot Dog', 'Com milho e batata palha', 18, 45, 10, 'produto', '/static/img/products/hotdog.jpg'),
(3, 'Wrap de Frango', 'Com salada fresca', 26, 30, 6, 'produto', '/static/img/products/wrap.jpg'),
(4, 'Açaí 400ml', 'Com granola e banana', 22, 40, 8, 'produto', '/static/img/products/acai.jpg'),
(4, 'Picolé', 'Sabores de frutas', 7, 80, 15, 'produto', '/static/img/products/picole.jpg'),
(5, 'Aluguel de Tenda', 'Diária na areia', 80, 999, 0, 'servico', '/static/img/products/tenda.jpg'),
(5, 'Cadeira Extra', 'Aluguel unitário', 15, 999, 0, 'servico', '/static/img/products/cadeira.jpg'),
(5, 'Guarda-sol Extra', 'Aluguel do dia', 20, 999, 0, 'servico', '/static/img/products/guarda.jpg'),
(5, 'Toalha', 'Aluguel limpa', 10, 999, 0, 'servico', '/static/img/products/toalha.jpg');

INSERT INTO reservations (tent_id, customer_name, customer_phone, date, time_slot, value, status)
SELECT id, 'Carlos Souza', '21988887777', CURRENT_DATE, 'dia todo', daily_price, 'confirmada'
FROM tents WHERE number = 5;

INSERT INTO reservations (tent_id, customer_name, customer_phone, date, time_slot, value, status)
SELECT id, 'Ana Silva', '11999990001', CURRENT_DATE + 1, 'manhã', daily_price, 'confirmada'
FROM tents WHERE number = 1;

COMMIT;
