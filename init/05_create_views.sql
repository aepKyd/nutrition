--
-- 05_create_views.sql
--
-- Создание представлений (VIEW) для упрощения доступа к данным и агрегации
--

SET search_path = nutrition, public;

-- 1. ingredients_active / ingredients_all
-- Активные ингредиенты (не удаленные)
CREATE OR REPLACE VIEW ingredients_active AS
SELECT *
FROM ingredients
WHERE deleted_at IS NULL;

-- Все ингредиенты (включая удаленные)
CREATE OR REPLACE VIEW ingredients_all AS
SELECT *
FROM ingredients;


-- 2. recipes_active / recipes_all
-- Активные рецепты (не удаленные)
CREATE OR REPLACE VIEW recipes_active AS
SELECT r.*, rc.name AS category_name
FROM recipes r
JOIN recipe_categories rc ON r.category_id = rc.id
WHERE r.deleted_at IS NULL;

-- Все рецепты (включая удаленные)
CREATE OR REPLACE VIEW recipes_all AS
SELECT r.*, rc.name AS category_name
FROM recipes r
JOIN recipe_categories rc ON r.category_id = rc.id;


-- 3. cooked_dishes_active / cooked_dishes_all
-- Активные приготовленные блюда (не удаленные)
CREATE OR REPLACE VIEW cooked_dishes_active AS
SELECT cd.*, r.name AS recipe_name, r.description AS recipe_description
FROM cooked_dishes cd
JOIN recipes r ON cd.recipe_id = r.id
WHERE cd.deleted_at IS NULL;

-- Все приготовленные блюда (включая удаленные)
CREATE OR REPLACE VIEW cooked_dishes_all AS
SELECT cd.*, r.name AS recipe_name, r.description AS recipe_description
FROM cooked_dishes cd
JOIN recipes r ON cd.recipe_id = r.id;


-- 4. recipe_nutrition (КБЖУ на весь рецепт)
CREATE OR REPLACE VIEW recipe_nutrition AS
SELECT
    r.id AS recipe_id,
    r.name AS recipe_name,
    SUM(ri.weight_grams * i.calories / 100) AS total_calories,
    SUM(ri.weight_grams * i.proteins / 100) AS total_proteins,
    SUM(ri.weight_grams * i.fats / 100) AS total_fats,
    SUM(ri.weight_grams * i.carbs / 100) AS total_carbs
FROM recipes r
JOIN recipe_ingredients ri ON r.id = ri.recipe_id
JOIN ingredients i ON ri.ingredient_id = i.id
GROUP BY r.id, r.name;


-- 5. cooked_dishes_per_100g (КБЖУ приготовленного блюда на 100г)
CREATE OR REPLACE VIEW cooked_dishes_per_100g AS
SELECT
    id,
    recipe_id,
    recipe_name,
    cooked_at,
    initial_weight,
    final_weight,
    remaining_weight,
    (total_calories / final_weight * 100) AS calories_per_100g,
    (total_proteins / final_weight * 100) AS proteins_per_100g,
    (total_fats / final_weight * 100) AS fats_per_100g,
    (total_carbs / final_weight * 100) AS carbs_per_100g
FROM cooked_dishes_active
WHERE final_weight > 0;


-- 6. remaining_dishes (Оставшиеся блюда)
CREATE OR REPLACE VIEW remaining_dishes AS
SELECT
    cd.id AS cooked_dish_id,
    cd.recipe_name,
    cd.cooked_at,
    cd.remaining_weight,
    cdp.calories_per_100g,
    cdp.proteins_per_100g,
    cdp.fats_per_100g,
    cdp.carbs_per_100g
FROM cooked_dishes_active cd
JOIN cooked_dishes_per_100g cdp ON cd.id = cdp.id
WHERE cd.remaining_weight > 0;


-- 7. daily_stats (Ежедневная статистика потребления)
CREATE OR REPLACE VIEW daily_stats AS
SELECT
    consumed_at::date AS consumption_date,
    meal_type,
    SUM(calories) AS total_calories,
    SUM(proteins) AS total_proteins,
    SUM(fats) AS total_fats,
    SUM(carbs) AS total_carbs,
    COUNT(id) AS total_portions
FROM consumed
GROUP BY consumed_at::date, meal_type
ORDER BY consumption_date, meal_type;


-- 8. popular_recipes (Самые популярные рецепты)
CREATE OR REPLACE VIEW popular_recipes AS
SELECT
    r.id AS recipe_id,
    r.name AS recipe_name,
    r.description AS recipe_description,
    r.times_cooked,
    r.avg_cooked_weight,
    (SELECT COUNT(*) FROM cooked_dishes cd WHERE cd.recipe_id = r.id AND cd.deleted_at IS NULL) as total_cooked_dishes_count
FROM recipes_active r
ORDER BY r.times_cooked DESC, total_cooked_dishes_count DESC;
