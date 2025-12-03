--
-- 03_create_indexes.sql
--
-- Создание индексов для повышения производительности и обеспечения целостности данных
--

SET search_path = nutrition, public;

-- 1. B-tree индексы на все внешние ключи (FK)
CREATE INDEX idx_ingredients_category_id ON ingredients (category_id);
CREATE INDEX idx_ingredient_synonyms_ingredient_id ON ingredient_synonyms (ingredient_id);
CREATE INDEX idx_recipes_category_id ON recipes (category_id);
CREATE INDEX idx_recipe_ingredients_recipe_id ON recipe_ingredients (recipe_id);
CREATE INDEX idx_recipe_ingredients_ingredient_id ON recipe_ingredients (ingredient_id);
CREATE INDEX idx_cooked_dishes_recipe_id ON cooked_dishes (recipe_id);
CREATE INDEX idx_cooked_dish_ingredients_cooked_dish_id ON cooked_dish_ingredients (cooked_dish_id);
CREATE INDEX idx_cooked_dish_ingredients_ingredient_id ON cooked_dish_ingredients (ingredient_id);
CREATE INDEX idx_consumed_cooked_dish_id ON consumed (cooked_dish_id);


-- 2. GIN trigram на ingredients.name_normalized для поиска по подстроке/нечеткого поиска
CREATE INDEX trgm_idx_ingredients_name_normalized ON ingredients USING GIN (name_normalized gin_trgm_ops);

-- 3. GIN trigram на ingredient_synonyms.synonym_normalized для поиска по синонимам
CREATE INDEX trgm_idx_ingredient_synonyms_synonym_normalized ON ingredient_synonyms USING GIN (synonym_normalized gin_trgm_ops);

-- 4. GIN full-text на ingredients.name для полнотекстового поиска
-- Предполагается наличие текстового поискового вектора, если его нет,
-- то нужно создать его через GENERATED COLUMN или TRIGGER
-- Для начала создадим базовый GIN индекс на name, если не используется tsvector
-- Если будет tsvector, то индекс будет на нем: CREATE INDEX fts_idx_ingredients_name ON ingredients USING GIN (to_tsvector('russian', name));
CREATE INDEX fts_idx_ingredients_name ON ingredients USING GIN (to_tsvector('russian', name));

-- 5. B-tree на consumed.consumed_at
CREATE INDEX idx_consumed_consumed_at ON consumed (consumed_at);

-- 6. Composite индекс на consumed(consumed_at, meal_type) для ускорения запросов по статистике потребления
CREATE INDEX idx_consumed_consumed_at_meal_type ON consumed (consumed_at, meal_type);

-- 7. B-tree на cooked_dishes.cooked_at
CREATE INDEX idx_cooked_dishes_cooked_at ON cooked_dishes (cooked_at);

-- 8. Partial indexes (WHERE deleted_at IS NULL) для активных записей
CREATE INDEX idx_ingredients_active ON ingredients (id) WHERE deleted_at IS NULL;
CREATE INDEX idx_recipes_active ON recipes (id) WHERE deleted_at IS NULL;
CREATE INDEX idx_cooked_dishes_active ON cooked_dishes (id) WHERE deleted_at IS NULL;
