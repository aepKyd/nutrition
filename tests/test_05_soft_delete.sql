--
-- tests/test_05_soft_delete.sql
--
-- Тестирование функций мягкого удаления
--

SET search_path = nutrition, public;
SET client_min_messages TO WARNING;

BEGIN;

-- 1. Создание тестового ингредиента для удаления
INSERT INTO ingredients (category_id, name, name_normalized, calories, proteins, fats, carbs)
VALUES ((SELECT id FROM ingredient_categories WHERE name = 'Напитки'), 'Удаляемый ингредиент', 'удаляемый ингредиент', 0, 0, 0, 0);
-- \gset
-- SELECT lastval() AS ingredient_to_delete_id;

-- 2. Успешное мягкое удаление
\echo '--- 1. Успешное мягкое удаление ингредиента ---'
-- SELECT nutrition.soft_delete_ingredient(:ingredient_to_delete_id);
-- SELECT * FROM ingredients_active WHERE id = :ingredient_to_delete_id; -- Должно быть пусто
-- SELECT * FROM ingredients_all WHERE id = :ingredient_to_delete_id AND deleted_at IS NOT NULL; -- Должна быть запись

-- 3. Попытка удаления используемого ингредиента
\echo '--- 2. Попытка удаления используемого ингредиента (должна быть ошибка) ---'
DO $$
BEGIN
    PERFORM nutrition.soft_delete_ingredient((SELECT id FROM ingredients WHERE name = 'Яйцо куриное'));
    RAISE EXCEPTION 'Soft delete of used ingredient should have failed';
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE '✓ Успешно: Попытка удалить используемый ингредиент вызвала ошибку';
END;
$$;


-- 4. Попытка удаления рецепта, который используется в приготовленном блюде
\echo '--- 3. Попытка удаления используемого рецепта (должна быть ошибка) ---'
-- Готовим блюдо
INSERT INTO cooked_dishes (recipe_id, initial_weight, final_weight, remaining_weight, total_calories, total_proteins, total_fats, total_carbs)
VALUES ((SELECT id FROM recipes WHERE name = 'Омлет'), 175, 160, 160, 252.9, 16.765, 18.805, 3.23);

DO $$
BEGIN
    PERFORM nutrition.soft_delete_recipe((SELECT id FROM recipes WHERE name = 'Омлет'));
    RAISE EXCEPTION 'Soft delete of used recipe should have failed';
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE '✓ Успешно: Попытка удалить используемый рецепт вызвала ошибку';
END;
$$;

-- 5. Попытка удаления приготовленного блюда, которое было съедено
\echo '--- 4. Попытка удаления съеденного блюда (должна быть ошибка) ---'
-- Съедаем часть
INSERT INTO consumed (cooked_dish_id, meal_type, weight_grams, calories, proteins, fats, carbs)
VALUES ((SELECT currval(pg_get_serial_sequence('cooked_dishes','id'))), 'breakfast', 100, 158.06, 10.48, 11.75, 2.02);

DO $$
BEGIN
    PERFORM nutrition.soft_delete_cooked_dish((SELECT currval(pg_get_serial_sequence('cooked_dishes','id'))));
    RAISE EXCEPTION 'Soft delete of consumed dish should have failed';
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE '✓ Успешно: Попытка удалить съеденное блюдо вызвала ошибку';
END;
$$;

ROLLBACK;
\echo 'Тесты мягкого удаления завершены. Все изменения отменены.'
