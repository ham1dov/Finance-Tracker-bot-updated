CREATE TABLE IF NOT EXISTS users(
    telegram_id BIGINT PRIMARY KEY,
    fullname VARCHAR(255),
    sex VARCHAR(10) CHECK (sex IN ('male', 'female')),
    social_status VARCHAR(50),
    language VARCHAR(5) CHECK (language IN ('en', 'uz', 'ru')),
    currency VARCHAR(5) CHECK (currency IN ('usd', 'eur', 'uzs', 'rub')),
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_earnings(
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(telegram_id) ON DELETE CASCADE,
    amount DECIMAL (12, 2),
    currency VARCHAR(5) CHECK (currency IN ('usd', 'uzs', 'rub', 'eur')),
    source VARCHAR(255),
    additional_info TEXT DEFAULT NULL,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_expenses(
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(telegram_id) ON DELETE CASCADE,
    amount DECIMAL(12, 2),
    currency VARCHAR(5) CHECK (currency IN ('usd', 'uzs', 'rub', 'eur')),
    source VARCHAR(20),
    additional_info TEXT DEFAULT NULL,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);