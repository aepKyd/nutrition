-- ============================================================================
-- Файл: 01_create_extensions.sql
-- Описание: Подключение расширений PostgreSQL и создание схемы
-- Дата создания: 2025-11-13
-- ============================================================================

-- Подключение расширений для нечёткого поиска
CREATE EXTENSION IF NOT EXISTS pg_trgm;        -- Trigram индексы
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;  -- Функции нечёткого сравнения
CREATE EXTENSION IF NOT EXISTS unaccent;       -- Удаление диакритических знаков

-- Создание схемы для изоляции объектов БД
CREATE SCHEMA IF NOT EXISTS nutrition;

-- Установка search_path для текущей сессии
SET search_path = nutrition, public;

-- Вывод информации об установленных расширениях
\echo '============================================'
\echo 'Extensions installed successfully:'
\echo '- pg_trgm (trigram indexes for fuzzy search)'
\echo '- fuzzystrmatch (fuzzy string matching)'
\echo '- unaccent (remove diacritical marks)'
\echo ''
\echo 'Schema created: nutrition'
\echo 'Search path set to: nutrition, public'
\echo '============================================'
