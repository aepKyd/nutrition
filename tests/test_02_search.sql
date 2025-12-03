--
-- tests/test_02_search.sql
--
-- Тестирование функции поиска search_ingredients
--

SET search_path = nutrition, public;
SET client_min_messages TO WARNING;

BEGIN;

-- 1. Точный поиск
-- Должен найти "Курица, грудка" с наивысшим score
\echo '--- 1. Точный поиск по "Курица, грудка" ---'
SELECT * FROM nutrition.search_ingredients('Курица, грудка', 1);


-- 2. Поиск с опечаткой
-- Должен найти "Гречневая крупа (сухая)"
\echo '--- 2. Поиск с опечаткой "гречкаа" ---'
SELECT * FROM nutrition.search_ingredients('гречкаа', 1);


-- 3. Поиск по синониму
-- Должен найти "Курица, грудка" по синониму "филе"
\echo '--- 3. Поиск по синониму "филе" ---'
SELECT * FROM nutrition.search_ingredients('филе', 5);


-- 4. Полнотекстовый поиск
-- Должен найти "Тунец консервированный в собств. соку"
\echo '--- 4. Полнотекстовый поиск "консервы из тунца" ---'
SELECT * FROM nutrition.search_ingredients('консервы из тунца', 1);


-- 5. Поиск по подстроке
-- Должен найти "Масло подсолнечное" и "Масло оливковое"
\echo '--- 5. Поиск по подстроке "масло" ---'
SELECT * FROM nutrition.search_ingredients('масло', 3);


ROLLBACK;
\echo 'Тесты поиска завершены. Все изменения отменены.'
