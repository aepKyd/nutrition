--
-- tests/test_03_calculations.sql
--
-- Тестирование логики расчетов КБЖУ
--

SET search_path = nutrition, public;
SET client_min_messages TO WARNING;

BEGIN;

-- 1. Создание тестового приготовленного блюда (Омлет)
INSERT INTO cooked_dishes (recipe_id, initial_weight, final_weight, remaining_weight, total_calories, total_proteins, total_fats, total_carbs)
VALUES (
    (SELECT id FROM recipes WHERE name = 'Омлет'),
    175, -- 120г яйца + 50г молока + 5г масла
    160, -- Предположим, что вес уменьшился после приготовления
    160,
    0, 0, 0, 0 -- КБЖУ будет пересчитано триггером
);
-- Получаем ID созданного блюда
-- \gset
-- SELECT lastval() AS last_dish_id;
-- DO $$
-- DECLARE
--    last_dish_id bigint;
-- BEGIN
--    last_dish_id := (SELECT currval(pg_get_serial_sequence('cooked_dishes','id')));

    -- 2. Добавление ингредиентов в приготовленное блюдо
INSERT INTO cooked_dish_ingredients (cooked_dish_id, ingredient_id, weight_grams, calories, proteins, fats, carbs)
    SELECT
        (SELECT currval(pg_get_serial_sequence('cooked_dishes','id'))),
        i.id,
        ri.weight_grams,
        i.calories,
        i.proteins,
        i.fats,
        i.carbs
    FROM recipe_ingredients ri
    JOIN ingredients i ON ri.ingredient_id = i.id
    WHERE ri.recipe_id = (SELECT id FROM recipes WHERE name = 'Омлет');
-- END;
-- $$;


-- 3. Проверка автоматического расчета КБЖУ блюда
--    Ожидаемые значения:
--    Яйцо (120г): 155 * 1.2 = 186 ккал, 12.7 * 1.2 = 15.24 п, 10.9 * 1.2 = 13.08 ф, 0.7 * 1.2 = 0.84 ц
--    Молоко (50г): 59 * 0.5 = 29.5 ккал, 3.0 * 0.5 = 1.5 п, 3.2 * 0.5 = 1.6 ф, 4.7 * 0.5 = 2.35 ц
--    Масло (5г): 748 * 0.05 = 37.4 ккал, 0.5 * 0.05 = 0.025 п, 82.5 * 0.05 = 4.125 ф, 0.8 * 0.05 = 0.04 ц
--    ИТОГО: 252.9 ккал, 16.765 п, 18.805 ф, 3.23 ц
\echo '--- 1. Проверка расчета КБЖУ для приготовленного блюда (Омлет) ---'
SELECT
    total_calories,
    total_proteins,
    total_fats,
    total_carbs
FROM cooked_dishes
WHERE id = (SELECT currval(pg_get_serial_sequence('cooked_dishes','id')));


-- 4. Потребление порции (100г)
INSERT INTO consumed (cooked_dish_id, meal_type, weight_grams)
VALUES ((SELECT currval(pg_get_serial_sequence('cooked_dishes','id'))), 'breakfast', 100);

-- 5. Проверка расчета КБЖУ для потребленной порции
--    Коэффициент: 100г / 160г = 0.625
--    Ожидаемые значения: 252.9 * 0.625 = 158.06 ккал, ...
\echo '--- 2. Проверка расчета КБЖУ для съеденной порции (100г Омлета) ---'
SELECT
    calories,
    proteins,
    fats,
    carbs
FROM consumed
WHERE id = (SELECT currval(pg_get_serial_sequence('consumed','id')));


-- 6. Проверка остатка блюда
\echo '--- 3. Проверка остатка блюда (должно быть 60г) ---'
SELECT remaining_weight FROM cooked_dishes WHERE id = (SELECT currval(pg_get_serial_sequence('cooked_dishes','id')));


-- 7. Проверка VIEW cooked_dishes_per_100g
--    КБЖУ на 100г = Общее КБЖУ / 160 * 100
\echo '--- 4. Проверка VIEW cooked_dishes_per_100g ---'
SELECT
    calories_per_100g,
    proteins_per_100g,
    fats_per_100g,
    carbs_per_100g
FROM cooked_dishes_per_100g
WHERE id = (SELECT currval(pg_get_serial_sequence('cooked_dishes','id')));


-- 8. Проверка VIEW daily_stats
\echo '--- 5. Проверка VIEW daily_stats ---'
SELECT * FROM daily_stats WHERE consumption_date = CURRENT_DATE;


ROLLBACK;
\echo 'Тесты расчетов завершены. Все изменения отменены.'
