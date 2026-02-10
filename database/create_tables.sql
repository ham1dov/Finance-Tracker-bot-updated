CREATE TABLE IF NOT EXISTS users(
    telegram_id BIGINT PRIMARY KEY,
    fullname VARCHAR(255),
    sex VARCHAR(10) CHECK (sex IN ('male', 'female')),
    social_status VARCHAR(50),
    language VARCHAR(5) CHECK (language IN ('en', 'uz', 'ru')),
    currency VARCHAR(5) CHECK (currency IN ('usd', 'eur', 'uzs', 'rub')),
    input_mode VARCHAR(10) DEFAULT 'bot' CHECK (input_mode IN ('bot', 'web')),
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_earnings(
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(telegram_id) ON DELETE CASCADE,
    amount DECIMAL (12, 2),
    currency VARCHAR(5) CHECK (currency IN ('usd', 'uzs', 'rub', 'eur')),
    source VARCHAR(255),
    payment_method VARCHAR(10) DEFAULT 'cash' CHECK (payment_method IN ('cash', 'card')),
    additional_info TEXT DEFAULT NULL,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_expenses(
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(telegram_id) ON DELETE CASCADE,
    amount DECIMAL(12, 2),
    currency VARCHAR(5) CHECK (currency IN ('usd', 'uzs', 'rub', 'eur')),
    source VARCHAR(255),
    payment_method VARCHAR(10) DEFAULT 'cash' CHECK (payment_method IN ('cash', 'card')),
    additional_info TEXT DEFAULT NULL,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS custom_categories(
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(telegram_id) ON DELETE CASCADE,
    type VARCHAR(10) CHECK (type IN ('income', 'expense')),
    name VARCHAR(255),
    emoji VARCHAR(10),
    UNIQUE(user_id, type, name)
);