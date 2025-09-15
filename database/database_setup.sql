-- MoMo Analytics MySQL Schema and Sample Data
-- This schema is designed to store and analyze mobile money transaction data.  It is designed to be used with the ETL pipeline.
-- It is designed to be used with the ETL pipeline.
-- Engine and charset defaults
SET NAMES utf8mb4;
SET time_zone = '+00:00';

-- Drop existing for idempotency
DROP TABLE IF EXISTS transaction_tags;
DROP TABLE IF EXISTS system_logs;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS transaction_categories;
DROP TABLE IF EXISTS users;

-- Users table
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'PK for users',
  phone VARCHAR(20) NOT NULL UNIQUE COMMENT 'E.164 or local format',
  full_name VARCHAR(120) NULL COMMENT 'Display name from SMS or enrichment',
  email VARCHAR(120) NULL COMMENT 'Optional email',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Row creation time',
  INDEX idx_users_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Transaction categories
CREATE TABLE transaction_categories (
  id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'PK for categories',
  name VARCHAR(60) NOT NULL UNIQUE COMMENT 'payment, transfer, withdrawal, deposit, ...',
  description VARCHAR(255) NULL COMMENT 'Human description',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_categories_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tags (free-form labeling)
CREATE TABLE tags (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(60) NOT NULL UNIQUE,
  description VARCHAR(255) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Transactions
CREATE TABLE transactions (
  id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT 'PK for transactions',
  external_ref VARCHAR(100) NULL UNIQUE COMMENT 'Deduplication key from SMS',
  occurred_at DATETIME NOT NULL COMMENT 'When the transaction happened',
  amount DECIMAL(12,2) NOT NULL COMMENT 'Transaction amount',
  currency VARCHAR(8) NOT NULL DEFAULT 'GHS' COMMENT 'Currency code',
  status ENUM('success','pending','failed') NOT NULL DEFAULT 'success' COMMENT 'Processing status',
  sender_id INT NOT NULL COMMENT 'FK to users',
  receiver_id INT NOT NULL COMMENT 'FK to users',
  category_id INT NOT NULL COMMENT 'FK to transaction_categories',
  channel VARCHAR(40) NULL COMMENT 'e.g., USSD, App, Agent',
  location VARCHAR(120) NULL COMMENT 'Optional geo/branch text',
  message_excerpt VARCHAR(255) NULL COMMENT 'Snippet from SMS',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Ingest time',
  CONSTRAINT fk_txn_sender FOREIGN KEY (sender_id) REFERENCES users(id),
  CONSTRAINT fk_txn_receiver FOREIGN KEY (receiver_id) REFERENCES users(id),
  CONSTRAINT fk_txn_category FOREIGN KEY (category_id) REFERENCES transaction_categories(id),
  INDEX idx_txn_occurred (occurred_at),
  INDEX idx_txn_sender (sender_id),
  INDEX idx_txn_receiver (receiver_id),
  INDEX idx_txn_category (category_id),
  INDEX idx_txn_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Junction: transaction ↔ tags (many-to-many)
CREATE TABLE transaction_tags (
  transaction_id BIGINT NOT NULL,
  tag_id INT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (transaction_id, tag_id),
  CONSTRAINT fk_ttx_txn FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
  CONSTRAINT fk_ttx_tag FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- System logs
CREATE TABLE system_logs (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  level ENUM('DEBUG','INFO','WARN','ERROR') NOT NULL DEFAULT 'INFO',
  source VARCHAR(60) NOT NULL COMMENT 'etl.parse, etl.clean, frontend, etc',
  message TEXT NOT NULL,
  transaction_id BIGINT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_log_txn FOREIGN KEY (transaction_id) REFERENCES transactions(id),
  INDEX idx_logs_level (level),
  INDEX idx_logs_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Sample data
INSERT INTO users (phone, full_name, email) VALUES
 ('+233200000001','Ama Mensah',NULL),
 ('+233200000002','Kofi Asare',NULL),
 ('+233200000003','Kojo Boateng',NULL),
 ('+233200000004','Akua Owusu',NULL),
 ('+233200000005','Yaw Adjei',NULL);

INSERT INTO transaction_categories (name, description) VALUES
 ('payment','Bill or merchant payments'),
 ('transfer','P2P transfers'),
 ('withdrawal','Cash out/ATM/agent'),
 ('deposit','Cash in/top-up');

INSERT INTO tags (name, description) VALUES
 ('utility','Electricity/water/internet'),
 ('fee','Transaction fee'),
 ('salary','Income payments'),
 ('reversal','Reversed transactions');

-- Insert transactions 
INSERT INTO transactions
 (external_ref, occurred_at, amount, currency, status, sender_id, receiver_id, category_id, channel, location, message_excerpt)
VALUES
 ('SMS-000001','2025-09-01 08:15:00',150.00,'GHS','success',1,2,2,'USSD','Accra','Transfer to +233200000002'),
 ('SMS-000002','2025-09-01 10:30:00',45.50,'GHS','success',1,3,1,'App','Kumasi','Paid utility bill'),
 ('SMS-000003','2025-09-02 12:00:00',500.00,'GHS','pending',4,1,2,'USSD','Takoradi','P2P transfer pending'),
 ('SMS-000004','2025-09-02 13:45:00',200.00,'GHS','success',5,4,4,'Agent','Accra','Cash deposit at agent'),
 ('SMS-000005','2025-09-03 09:20:00',100.00,'GHS','failed',2,5,3,'Agent','Cape Coast','Withdrawal failed');

-- Label a few transactions
INSERT INTO transaction_tags (transaction_id, tag_id) VALUES
  (1,2), -- fee
  (2,1), -- utility
  (3,4); -- reversal

-- Sample logs
INSERT INTO system_logs (level, source, message, transaction_id) VALUES
 ('INFO','etl.parse','Parsed 100 SMS messages',NULL),
 ('WARN','etl.clean','Found malformed date; used fallback',3),
 ('ERROR','etl.load','Failed to insert transaction',5);

-- Basic CRUD checks
-- R: list recent transactions with users and category
SELECT t.id, t.amount, t.status, t.occurred_at,
       su.full_name AS sender, ru.full_name AS receiver,
       c.name AS category
FROM transactions t
JOIN users su ON su.id = t.sender_id
JOIN users ru ON ru.id = t.receiver_id
JOIN transaction_categories c ON c.id = t.category_id
ORDER BY t.occurred_at DESC
LIMIT 10;

-- C: insert a new transaction
INSERT INTO transactions (occurred_at, amount, currency, status, sender_id, receiver_id, category_id, channel)
VALUES (NOW(), 75.25, 'GHS', 'success', 1, 2, 2, 'App');

-- U: update status
UPDATE transactions SET status = 'success' WHERE external_ref = 'SMS-000003';

-- D: delete a tag relation
DELETE FROM transaction_tags WHERE transaction_id = 1 AND tag_id = 2;


