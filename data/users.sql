-- Sample data for practice. Recreate data/users.db with either:
--   go run ./cmd/users -db data/users.db load data/users.sql
--   sqlite3 data/users.db < data/users.sql
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    username   TEXT    NOT NULL UNIQUE,
    full_name  TEXT    NOT NULL,
    email      TEXT    NOT NULL UNIQUE,
    phone      TEXT,
    age        INTEGER,
    city       TEXT,
    status     TEXT    NOT NULL DEFAULT 'active', -- active | inactive | blocked
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE accounts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(id),
    account_no TEXT    NOT NULL UNIQUE,
    type       TEXT    NOT NULL,                 -- savings | current | fixed
    currency   TEXT    NOT NULL DEFAULT 'LAK',
    balance    INTEGER NOT NULL DEFAULT 0
);

INSERT INTO users (username, full_name, email, phone, age, city, status, created_at) VALUES
  ('somchai',     'Somchai Phommavong',     'somchai@example.com',     '02055512345', 34,   'Vientiane',     'active',   '2023-01-15 09:12:00'),
  ('khamla',      'Khamla Sisouphanh',      'khamla@example.com',      '02077788899', 28,   'Luang Prabang', 'active',   '2023-02-03 14:30:00'),
  ('bounmy',      'Bounmy Keomany',         'bounmy@example.com',      '02023456789', 45,   'Pakse',         'inactive', '2023-03-21 10:05:00'),
  ('vilayphone',  'Vilayphone Inthavong',   'vilayphone@example.com',  NULL,          31,   'Vientiane',     'active',   '2023-05-09 08:45:00'),
  ('souksavanh',  'Souksavanh Douangchanh', 'souksavanh@example.com',  '02099911122', 52,   'Savannakhet',   'active',   '2023-06-30 16:20:00'),
  ('phonesavanh', 'Phonesavanh Vongsa',     'phonesavanh@example.com', '02055500011', 23,   'Vientiane',     'blocked',  '2023-08-14 11:10:00'),
  ('noy',         'Noy Sengdara',           'noy@example.com',         '02088877766', NULL, 'Thakhek',       'active',   '2023-09-02 13:00:00'),
  ('kongkeo',     'Kongkeo Saysana',        'kongkeo@example.com',     '02066655544', 39,   'Luang Prabang', 'active',   '2023-11-27 09:55:00'),
  ('manivanh',    'Manivanh Chanthala',     'manivanh@example.com',    '02044433322', 27,   'Pakse',         'inactive', '2024-01-08 15:40:00'),
  ('sengphet',    'Sengphet Luangrath',     'sengphet@example.com',    '02012312312', 61,   'Vientiane',     'active',   '2024-02-19 10:25:00'),
  ('latsamy',     'Latsamy Phanthavong',    'latsamy@example.com',     '02032132132', 19,   'Savannakhet',   'active',   '2024-04-11 17:05:00'),
  ('thongchanh',  'Thongchanh Sisavath',    'thongchanh@example.com',  NULL,          47,   'Vientiane',     'blocked',  '2024-06-23 08:15:00'),
  ('ketsana',     'Ketsana Vongphachanh',   'ketsana@example.com',     '02065465465', 35,   'Luang Prabang', 'active',   '2024-08-05 12:35:00'),
  ('daovone',     'Daovone Xaysongkham',    'daovone@example.com',     '02098798798', 29,   NULL,            'active',   '2024-10-17 09:00:00'),
  ('anousone',    'Anousone Keovongsa',     'anousone@example.com',    '02074174174', 55,   'Pakse',         'active',   '2025-01-29 14:50:00');

INSERT INTO accounts (user_id, account_no, type, currency, balance) VALUES
  (1,  '1000000001', 'savings', 'LAK', 25000000),
  (1,  '1000000002', 'current', 'LAK',  8500000),
  (2,  '1000000003', 'savings', 'LAK', 12300000),
  (3,  '1000000004', 'savings', 'LAK',   450000),
  (4,  '1000000005', 'savings', 'LAK', 31000000),
  (4,  '1000000006', 'fixed',   'USD',     5000),
  (5,  '1000000007', 'fixed',   'LAK', 150000000),
  (5,  '1000000008', 'current', 'LAK', 22000000),
  (6,  '1000000009', 'savings', 'LAK',   1200000),
  (7,  '1000000010', 'savings', 'LAK',   9800000),
  (8,  '1000000011', 'current', 'LAK', 47500000),
  (9,  '1000000012', 'savings', 'LAK',   3100000),
  (10, '1000000013', 'fixed',   'LAK', 88000000),
  (10, '1000000014', 'savings', 'USD',     1200),
  (11, '1000000015', 'savings', 'LAK',    750000),
  (13, '1000000016', 'savings', 'LAK', 16400000),
  (14, '1000000017', 'current', 'LAK',  5600000),
  (15, '1000000018', 'savings', 'LAK', 64000000),
  (15, '1000000019', 'fixed',   'LAK', 120000000);
