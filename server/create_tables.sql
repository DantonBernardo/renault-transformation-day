-- Script para criar as tabelas necessárias no SQLite
-- Execute: sqlite3 database/database.sqlite < create_tables.sql

-- Tabela de migrações
CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    migration VARCHAR(255) NOT NULL,
    batch INTEGER NOT NULL
);

-- Tabela group_of_three
CREATE TABLE IF NOT EXISTS group_of_three (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cube_1 INTEGER,
    cube_2 INTEGER,
    cube_3 INTEGER,
    group_time DECIMAL(8,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela cubes
CREATE TABLE IF NOT EXISTS cubes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    color VARCHAR(255) NOT NULL,
    face VARCHAR(255) NOT NULL,
    individual_time DECIMAL(8,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES group_of_three(id) ON DELETE CASCADE
);

-- Insere registros de migração para evitar problemas
INSERT OR IGNORE INTO migrations (migration, batch) VALUES 
('0001_01_01_000000_create_users_table', 1),
('0001_01_01_000001_create_cache_table', 1),
('0001_01_01_000002_create_jobs_table', 1),
('2025_10_17_165145_create_cubes_table', 1),
('2025_10_17_165210_create_group_of_three_table', 1);

-- Verifica se as tabelas foram criadas
SELECT 'Tabelas criadas com sucesso!' as status;
SELECT name FROM sqlite_master WHERE type='table';
