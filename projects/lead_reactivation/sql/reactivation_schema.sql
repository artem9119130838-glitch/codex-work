-- Миграция базы данных v4: Создание таблицы истории реанимации клиентов

CREATE TABLE IF NOT EXISTS client_reactivation_history (
    id SERIAL PRIMARY KEY,
    client_email VARCHAR(255) NOT NULL,
    article_url TEXT NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    template_used VARCHAR(100),
    FOREIGN KEY (client_email) REFERENCES clients_intel(email) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_reactivation_email ON client_reactivation_history(client_email);
