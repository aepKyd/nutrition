--
-- tests/test_04_triggers.sql
--
-- Тестирование триггеров
--

SET search_path = nutrition, public;
SET client_min_messages TO WARNING;

BEGIN;

-- 1. Тест триггера нормализации имени (trg_normalize_ingredient_name)
\echo '--- 1. Тест триггера нормализации имени ---'
INSERT INTO ingredients (category_id, name, name_normalized, calories, proteins, fats, carbs)
VALUES ((SELECT id FROM ingredient_categories WHERE name = 'Напитки'), '  Кофе с Молоком  (Латте) ', '', 50, 3, 3, 3);

SELECT name_normalized FROM ingredients WHERE name_normalized = 'кофе с молоком (латте)';


-- 2. Тест триггера обновления updated_at (trg_update_recipe_updated_at)
\echo '--- 2. Тест триггера обновления updated_at ---'
-- Запоминаем старое время
-- \gset
-- SELECT updated_at AS old_updated_at FROM recipes WHERE name = 'Омлет';
-- Ждем 1 секунду, чтобы гарантировать разницу во времени
-- SELECT pg_sleep(1);
-- UPDATE recipes SET description = 'Новое описание' WHERE name = 'Омлет';
-- SELECT updated_at > :old_updated_at AS updated FROM recipes WHERE name = 'Омлет';


-- 3. Тест триггера урезания порции до остатка (trg_calculate_consumed_nutrition)
\echo '--- 3. Тест триггера урезания порции до остатка ---'
-- Создаем блюдо
INSERT INTO cooked_dishes (recipe_id, initial_weight, final_weight, remaining_weight, total_calories, total_proteins, total_fats, total_carbs)
VALUES ((SELECT id FROM recipes WHERE name = 'Омлет'), 175, 160, 10, 252.9, 16.765, 18.805, 3.23);

-- Пытаемся съесть больше, чем есть (20г), порция должна урезаться до 10г
INSERT INTO consumed (cooked_dish_id, meal_type, weight_grams)
VALUES ((SELECT currval(pg_get_serial_sequence('cooked_dishes','id'))), 'snack', 20);

SELECT weight_grams FROM consumed WHERE id = (SELECT currval(pg_get_serial_sequence('consumed','id')));


-- 4. Тест триггера статистики рецепта (trg_update_recipe_stats)
\echo '--- 4. Тест триггера статистики рецепта ---'
-- \gset
-- SELECT times_cooked AS old_times_cooked FROM recipes WHERE name = 'Гречка с курицей';
-- Готовим блюдо
INSERT INTO cooked_dishes (recipe_id, initial_weight, final_weight, remaining_weight, total_calories, total_proteins, total_fats, total_carbs)
VALUES ((SELECT id FROM recipes WHERE name = 'Гречка с курицей'), 255, 250, 250, 0, 0, 0, 0);

-- Проверяем, что счетчик увеличился
-- SELECT times_cooked > :old_times_cooked AS updated_stat FROM recipes WHERE name = 'Гречка с курицей';


ROLLBACK;
\echo 'Тесты триггеров завершены. Все изменения отменены.'
