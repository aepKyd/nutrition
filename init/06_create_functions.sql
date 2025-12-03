--
-- 06_create_functions.sql
--
-- Создание функций для работы с данными
--

SET search_path = nutrition, public;

-- 1. search_ingredients(TEXT, INT) — многоуровневый поиск
-- Ищет ингредиенты по названию или синонимам, используя полнотекстовый поиск и trigram-совпадение.
-- Возвращает список ингредиентов, отсортированных по релевантности.
CREATE OR REPLACE FUNCTION nutrition.search_ingredients(
    p_search_query TEXT,
    p_limit INT DEFAULT 10
)
RETURNS TABLE (
    id INT,
    name VARCHAR(200),
    category_name VARCHAR(100),
    search_score NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        i.id,
        i.name,
        ic.name AS category_name,
        -- Чем выше score, тем релевантнее
        (
            -- Точное совпадение
            CASE WHEN LOWER(i.name) = LOWER(p_search_query) THEN 10.0 ELSE 0.0 END +
            -- Совпадение по нормализованному имени
            CASE WHEN LOWER(i.name_normalized) = LOWER(p_search_query) THEN 9.0 ELSE 0.0 END +
            -- Полнотекстовый поиск (чем больше совпадений, тем выше ранг)
            ts_rank(to_tsvector('russian', i.name), websearch_to_tsquery('russian', p_search_query)) * 5.0 +
            -- Триграмное сходство для name_normalized
            similarity(i.name_normalized, p_search_query) * 3.0 +
            -- Поиск по синонимам
            COALESCE((SELECT MAX(similarity(s.synonym_normalized, p_search_query)) FROM nutrition.ingredient_synonyms s WHERE s.ingredient_id = i.id), 0) * 2.0
        )::NUMERIC AS score
    FROM
        nutrition.ingredients i
    JOIN
        nutrition.ingredient_categories ic ON i.category_id = ic.id
    WHERE
        i.deleted_at IS NULL AND (
            LOWER(i.name) LIKE '%' || LOWER(p_search_query) || '%' OR
            LOWER(i.name_normalized) LIKE '%' || LOWER(p_search_query) || '%' OR
            to_tsvector('russian', i.name) @@ websearch_to_tsquery('russian', p_search_query) OR
            similarity(i.name_normalized, p_search_query) > 0.1 OR -- Произвольный порог
            EXISTS (SELECT 1 FROM nutrition.ingredient_synonyms s WHERE s.ingredient_id = i.id AND similarity(s.synonym_normalized, p_search_query) > 0.1)
        )
    ORDER BY
        score DESC
    LIMIT p_limit;
END;
$$;


-- 2. calculate_dish_nutrition(BIGINT) — ручной расчёт КБЖУ для конкретного приготовленного блюда
CREATE OR REPLACE FUNCTION nutrition.calculate_dish_nutrition(
    p_cooked_dish_id BIGINT
)
RETURNS TABLE (
    total_calories NUMERIC(10, 2),
    total_proteins NUMERIC(10, 2),
    total_fats NUMERIC(10, 2),
    total_carbs NUMERIC(10, 2),
    initial_weight NUMERIC(10, 2)
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        SUM(cdi.calories / 100 * cdi.weight_grams),
        SUM(cdi.proteins / 100 * cdi.weight_grams),
        SUM(cdi.fats / 100 * cdi.weight_grams),
        SUM(cdi.carbs / 100 * cdi.weight_grams),
        SUM(cdi.weight_grams)
    FROM
        nutrition.cooked_dish_ingredients cdi
    WHERE
        cdi.cooked_dish_id = p_cooked_dish_id;
END;
$$;


-- 3. get_daily_summary(DATE) — JSON статистика за день
CREATE OR REPLACE FUNCTION nutrition.get_daily_summary(
    p_date DATE
)
RETURNS JSONB
LANGUAGE sql
AS $$
    WITH daily_totals AS (
        SELECT
            COALESCE(SUM(calories), 0) AS total_calories,
            COALESCE(SUM(proteins), 0) AS total_proteins,
            COALESCE(SUM(fats), 0) AS total_fats,
            COALESCE(SUM(carbs), 0) AS total_carbs
        FROM nutrition.consumed
        WHERE consumed_at::date = p_date
    ),
    meal_data AS (
        SELECT
            meal_type,
            SUM(calories) AS calories,
            SUM(proteins) AS proteins,
            SUM(fats) AS fats,
            SUM(carbs) AS carbs,
            COUNT(id) AS portions_count
        FROM nutrition.consumed
        WHERE consumed_at::date = p_date
        GROUP BY meal_type
    )
    SELECT jsonb_build_object(
        'date', p_date,
        'total_nutrition', jsonb_build_object(
            'calories', (SELECT total_calories FROM daily_totals),
            'proteins', (SELECT total_proteins FROM daily_totals),
            'fats', (SELECT total_fats FROM daily_totals),
            'carbs', (SELECT total_carbs FROM daily_totals)
        ),
        'meals', (SELECT jsonb_agg(meal_data ORDER BY meal_type) FROM meal_data)
    );
$$;


-- 4. soft_delete_ingredient(INT) — мягкое удаление ингредиента с проверкой использования
CREATE OR REPLACE FUNCTION nutrition.soft_delete_ingredient(
    p_ingredient_id INT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    -- Проверка на использование в recipe_ingredients
    IF EXISTS (SELECT 1 FROM nutrition.recipe_ingredients WHERE ingredient_id = p_ingredient_id) THEN
        RAISE EXCEPTION 'Ингредиент с ID % используется в рецептах и не может быть удален.', p_ingredient_id;
    END IF;

    -- Проверка на использование в cooked_dish_ingredients
    IF EXISTS (SELECT 1 FROM nutrition.cooked_dish_ingredients WHERE ingredient_id = p_ingredient_id) THEN
        RAISE EXCEPTION 'Ингредиент с ID % используется в приготовленных блюдах и не может быть удален.', p_ingredient_id;
    END IF;

    UPDATE nutrition.ingredients
    SET deleted_at = NOW()
    WHERE id = p_ingredient_id;
END;
$$;


-- 5. soft_delete_recipe(INT) — мягкое удаление рецепта
CREATE OR REPLACE FUNCTION nutrition.soft_delete_recipe(
    p_recipe_id INT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    -- Проверка на использование в cooked_dishes (активные, не удаленные)
    IF EXISTS (SELECT 1 FROM nutrition.cooked_dishes WHERE recipe_id = p_recipe_id AND deleted_at IS NULL) THEN
        RAISE EXCEPTION 'Рецепт с ID % используется в активных приготовленных блюдах и не может быть удален.', p_recipe_id;
    END IF;

    UPDATE nutrition.recipes
    SET deleted_at = NOW()
    WHERE id = p_recipe_id;
END;
$$;


-- 6. soft_delete_cooked_dish(BIGINT) — мягкое удаление приготовленного блюда с проверкой остатка
CREATE OR REPLACE FUNCTION nutrition.soft_delete_cooked_dish(
    p_cooked_dish_id BIGINT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_remaining_weight NUMERIC(10, 2);
BEGIN
    SELECT remaining_weight INTO v_remaining_weight
    FROM nutrition.cooked_dishes
    WHERE id = p_cooked_dish_id;

    IF v_remaining_weight IS NULL THEN
        RAISE EXCEPTION 'Приготовленное блюдо с ID % не найдено.', p_cooked_dish_id;
    END IF;

    IF v_remaining_weight < (SELECT cd.final_weight FROM nutrition.cooked_dishes cd WHERE cd.id = p_cooked_dish_id) THEN
        -- Если remaining_weight меньше final_weight, значит, часть блюда была потреблена
        RAISE EXCEPTION 'Блюдо с ID % было частично или полностью потреблено и не может быть удалено.', p_cooked_dish_id;
    END IF;

    UPDATE nutrition.cooked_dishes
    SET deleted_at = NOW()
    WHERE id = p_cooked_dish_id;
END;
$$;