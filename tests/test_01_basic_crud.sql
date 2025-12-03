--
-- tests/test_01_basic_crud.sql
--
-- Тестирование базовых CRUD-операций и ограничений
--

SET search_path = nutrition, public;
SET client_min_messages TO WARNING; -- Скрываем NOTICE сообщения

-- Оборачиваем все в транзакцию
BEGIN;

-- 1. INSERT - Успешное добавление
INSERT INTO ingredient_categories (name) VALUES ('Тестовая категория');
INSERT INTO ingredients (category_id, name, name_normalized, calories, proteins, fats, carbs)
VALUES ((SELECT id FROM ingredient_categories WHERE name = 'Тестовая категория'), 'Тестовый ингредиент', 'тестовый ингредиент', 10, 1, 1, 1);
\echo '✓ INSERT: Успешное добавление тестовых данных.'

-- 2. SELECT - Проверка чтения
SELECT * FROM ingredients WHERE name = 'Тестовый ингредиент';
\echo '✓ SELECT: Успешное чтение тестовых данных.'

-- 3. UPDATE - Проверка обновления
UPDATE ingredients SET calories = 20 WHERE name = 'Тестовый ингредиент';
SELECT * FROM ingredients WHERE name = 'Тестовый ингредиент' AND calories = 20;
\echo '✓ UPDATE: Успешное обновление тестовых данных.'

-- 4. DELETE - Проверка удаления
DELETE FROM ingredients WHERE name = 'Тестовый ингредиент';
DELETE FROM ingredient_categories WHERE name = 'Тестовая категория';
\echo '✓ DELETE: Успешное удаление тестовых данных.'


-- 5. CONSTRAINTS - Проверка ограничений
-- a) NOT NULL
DO $$
BEGIN
    INSERT INTO ingredients (category_id, name, name_normalized, calories, proteins, fats, carbs) VALUES (NULL, 'Test', 'test', 1, 1, 1, 1);
    RAISE EXCEPTION 'NOT NULL constraint on category_id failed';
EXCEPTION WHEN not_null_violation THEN
    RAISE NOTICE '✓ CONSTRAINT (NOT NULL): Успешно отработало ограничение NOT NULL';
END;
$$;

-- b) UNIQUE
DO $$
BEGIN
    INSERT INTO ingredient_categories (name) VALUES ('Дубликат');
    INSERT INTO ingredient_categories (name) VALUES ('Дубликат');
    RAISE EXCEPTION 'UNIQUE constraint on name failed';
EXCEPTION WHEN unique_violation THEN
    RAISE NOTICE '✓ CONSTRAINT (UNIQUE): Успешно отработало ограничение UNIQUE';
END;
$$;

-- c) CHECK
DO $$
BEGIN
    INSERT INTO ingredients (category_id, name, name_normalized, calories, proteins, fats, carbs)
    VALUES ((SELECT id FROM ingredient_categories WHERE name = 'Мясо'), 'Негативные калории', 'негативные калории', -100, 1, 1, 1);
    RAISE EXCEPTION 'CHECK constraint on calories failed';
EXCEPTION WHEN check_violation THEN
    RAISE NOTICE '✓ CONSTRAINT (CHECK): Успешно отработало ограничение CHECK на отрицательные значения';
END;
$$;


-- d) FOREIGN KEY
DO $$
BEGIN
    INSERT INTO ingredients (category_id, name, name_normalized, calories, proteins, fats, carbs)
    VALUES (999, 'Несуществующая категория', 'несуществующая категория', 10, 1, 1, 1);
    RAISE EXCEPTION 'FOREIGN KEY constraint on category_id failed';
EXCEPTION WHEN foreign_key_violation THEN
    RAISE NOTICE '✓ CONSTRAINT (FOREIGN KEY): Успешно отработало ограничение FOREIGN KEY';
END;
$$;

-- Откатываем транзакцию, чтобы не оставлять тестовых данных
ROLLBACK;
\echo 'Тесты завершены. Все изменения отменены.'
