--
-- 02_create_tables.sql
--
-- Создание таблиц в схеме nutrition
--

-- Устанавливаем путь поиска для всех последующих команд в сессии
SET search_path = nutrition, public;

-- 1. Категории ингредиентов
CREATE TABLE ingredient_categories (
    id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

COMMENT ON TABLE ingredient_categories IS 'Категории ингредиентов (например, "Мясо", "Рыба", "Овощи")';
COMMENT ON COLUMN ingredient_categories.id IS 'Уникальный идентификатор категории';
COMMENT ON COLUMN ingredient_categories.name IS 'Название категории';
COMMENT ON COLUMN ingredient_categories.description IS 'Подробное описание категории';


-- 2. Категории рецептов
CREATE TABLE recipe_categories (
    id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

COMMENT ON TABLE recipe_categories IS 'Категории рецептов (например, "Завтрак", "Обед", "Супы")';
COMMENT ON COLUMN recipe_categories.id IS 'Уникальный идентификатор категории';
COMMENT ON COLUMN recipe_categories.name IS 'Название категории';
COMMENT ON COLUMN recipe_categories.description IS 'Подробное описание категории';


-- 3. Ингредиенты
CREATE TABLE ingredients (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_id SMALLINT NOT NULL,
    name VARCHAR(200) NOT NULL UNIQUE,
    name_normalized VARCHAR(200) NOT NULL UNIQUE,

    -- Пищевая ценность на 100г
    calories NUMERIC(8, 2) NOT NULL CHECK (calories >= 0), -- ккал
    proteins NUMERIC(8, 2) NOT NULL CHECK (proteins >= 0), -- г
    fats NUMERIC(8, 2) NOT NULL CHECK (fats >= 0),         -- г
    carbs NUMERIC(8, 2) NOT NULL CHECK (carbs >= 0),      -- г

    -- Дополнительные микроэлементы (опционально)
    fiber NUMERIC(8, 2) CHECK (fiber >= 0),      -- клетчатка, г
    sugar NUMERIC(8, 2) CHECK (sugar >= 0),      -- сахар, г
    sodium NUMERIC(8, 2) CHECK (sodium >= 0),    -- натрий, мг
    potassium NUMERIC(8, 2) CHECK (potassium >= 0), -- калий, мг
    calcium NUMERIC(8, 2) CHECK (calcium >= 0),    -- кальций, мг
    iron NUMERIC(8, 2) CHECK (iron >= 0),        -- железо, мг
    vitamin_a NUMERIC(8, 2) CHECK (vitamin_a >= 0), -- мкг
    vitamin_c NUMERIC(8, 2) CHECK (vitamin_c >= 0), -- мг
    vitamin_d NUMERIC(8, 2) CHECK (vitamin_d >= 0), -- мкг

    -- Метаданные
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,

    -- Связи
    CONSTRAINT fk_ingredient_category
        FOREIGN KEY(category_id)
        REFERENCES ingredient_categories(id)
);

COMMENT ON TABLE ingredients IS 'Справочник всех ингредиентов с их пищевой ценностью на 100г';
COMMENT ON COLUMN ingredients.id IS 'Уникальный идентификатор ингредиента';
COMMENT ON COLUMN ingredients.category_id IS 'Ссылка на категорию ингредиента';
COMMENT ON COLUMN ingredients.name IS 'Полное название ингредиента';
COMMENT ON COLUMN ingredients.name_normalized IS 'Нормализованное название для поиска (lower, trim, no-ё)';
COMMENT ON COLUMN ingredients.calories IS 'Калорийность на 100г (ккал)';
COMMENT ON COLUMN ingredients.proteins IS 'Белки на 100г (г)';
COMMENT ON COLUMN ingredients.fats IS 'Жиры на 100г (г)';
COMMENT ON COLUMN ingredients.carbs IS 'Углеводы на 100г (г)';
COMMENT ON COLUMN ingredients.fiber IS 'Клетчатка на 100г (г)';
COMMENT ON COLUMN ingredients.sugar IS 'Сахар на 100г (г)';
COMMENT ON COLUMN ingredients.sodium IS 'Натрий на 100г (мг)';
COMMENT ON COLUMN ingredients.potassium IS 'Калий на 100г (мг)';
COMMENT ON COLUMN ingredients.calcium IS 'Кальций на 100г (мг)';
COMMENT ON COLUMN ingredients.iron IS 'Железо на 100г (мг)';
COMMENT ON COLUMN ingredients.vitamin_a IS 'Витамин A на 100г (мкг)';
COMMENT ON COLUMN ingredients.vitamin_c IS 'Витамин C на 100г (мг)';
COMMENT ON COLUMN ingredients.vitamin_d IS 'Витамин D на 100г (мкг)';
COMMENT ON COLUMN ingredients.created_at IS 'Время создания записи';
COMMENT ON COLUMN ingredients.updated_at IS 'Время последнего обновления записи';
COMMENT ON COLUMN ingredients.deleted_at IS 'Время мягкого удаления записи';

-- 4. Синонимы ингредиентов
CREATE TABLE ingredient_synonyms (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ingredient_id INT NOT NULL,
    synonym VARCHAR(200) NOT NULL,
    synonym_normalized VARCHAR(200) NOT NULL UNIQUE,

    CONSTRAINT fk_synonym_ingredient
        FOREIGN KEY(ingredient_id)
        REFERENCES ingredients(id)
        ON DELETE CASCADE,

    UNIQUE (ingredient_id, synonym)
);

COMMENT ON TABLE ingredient_synonyms IS 'Синонимы для названий ингредиентов для улучшения поиска';
COMMENT ON COLUMN ingredient_synonyms.id IS 'Уникальный идентификатор синонима';
COMMENT ON COLUMN ingredient_synonyms.ingredient_id IS 'Ссылка на исходный ингредиент';
COMMENT ON COLUMN ingredient_synonyms.synonym IS 'Синоним названия';
COMMENT ON COLUMN ingredient_synonyms.synonym_normalized IS 'Нормализованный синоним';


-- 5. Рецепты
CREATE TABLE recipes (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_id SMALLINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    instructions TEXT,

    -- Статистика использования
    times_cooked INT NOT NULL DEFAULT 0,
    avg_cooked_weight NUMERIC(10, 2),

    -- Метаданные
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,

    CONSTRAINT fk_recipe_category
        FOREIGN KEY(category_id)
        REFERENCES recipe_categories(id)
);

COMMENT ON TABLE recipes IS 'Рецепты блюд, состоящие из ингредиентов';
COMMENT ON COLUMN recipes.id IS 'Уникальный идентификатор рецепта';
COMMENT ON COLUMN recipes.category_id IS 'Ссылка на категорию рецепта';
COMMENT ON COLUMN recipes.name IS 'Название рецепта';
COMMENT ON COLUMN recipes.description IS 'Краткое описание рецепта';
COMMENT ON COLUMN recipes.instructions IS 'Инструкции по приготовлению';
COMMENT ON COLUMN recipes.times_cooked IS 'Счетчик, сколько раз блюдо было приготовлено';
COMMENT ON COLUMN recipes.avg_cooked_weight IS 'Средний вес приготовленного блюда';
COMMENT ON COLUMN recipes.created_at IS 'Время создания записи';
COMMENT ON COLUMN recipes.updated_at IS 'Время последнего обновления записи';
COMMENT ON COLUMN recipes.deleted_at IS 'Время мягкого удаления записи';


-- 6. Ингредиенты в рецептах (связующая таблица)
CREATE TABLE recipe_ingredients (
    recipe_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    weight_grams NUMERIC(10, 2) NOT NULL CHECK (weight_grams > 0),

    PRIMARY KEY (recipe_id, ingredient_id),

    CONSTRAINT fk_recipe
        FOREIGN KEY(recipe_id)
        REFERENCES recipes(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_ingredient
        FOREIGN KEY(ingredient_id)
        REFERENCES ingredients(id)
        ON DELETE RESTRICT -- Запрещаем удалять ингредиент, если он используется в рецепте
);

COMMENT ON TABLE recipe_ingredients IS 'Связующая таблица для рецептов и ингредиентов';
COMMENT ON COLUMN recipe_ingredients.recipe_id IS 'Ссылка на рецепт';
COMMENT ON COLUMN recipe_ingredients.ingredient_id IS 'Ссылка на ингредиент';
COMMENT ON COLUMN recipe_ingredients.weight_grams IS 'Вес ингредиента в рецепте (в граммах)';


-- 7. Приготовленные блюда (факты)
CREATE TABLE cooked_dishes (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    recipe_id INT NOT NULL,
    cooked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Исходные и фактические веса
    initial_weight NUMERIC(10, 2) NOT NULL, -- Сумма весов ингредиентов
    final_weight NUMERIC(10, 2) NOT NULL, -- Вес после приготовления
    remaining_weight NUMERIC(10, 2) NOT NULL CHECK (remaining_weight >= 0),

    -- Пищевая ценность на всё блюдо
    total_calories NUMERIC(10, 2) NOT NULL,
    total_proteins NUMERIC(10, 2) NOT NULL,
    total_fats NUMERIC(10, 2) NOT NULL,
    total_carbs NUMERIC(10, 2) NOT NULL,

    -- Метаданные
    deleted_at TIMESTAMPTZ,

    CONSTRAINT fk_cooked_dish_recipe
        FOREIGN KEY(recipe_id)
        REFERENCES recipes(id)
);

COMMENT ON TABLE cooked_dishes IS 'Факты приготовления блюд по рецептам';
COMMENT ON COLUMN cooked_dishes.id IS 'Уникальный идентификатор факта приготовления';
COMMENT ON COLUMN cooked_dishes.recipe_id IS 'Ссылка на использованный рецепт';
COMMENT ON COLUMN cooked_dishes.cooked_at IS 'Время приготовления';
COMMENT ON COLUMN cooked_dishes.initial_weight IS 'Суммарный вес сырых ингредиентов';
COMMENT ON COLUMN cooked_dishes.final_weight IS 'Финальный вес блюда после ужарки/уварки';
COMMENT ON COLUMN cooked_dishes.remaining_weight IS 'Оставшийся вес блюда, доступный для потребления';
COMMENT ON COLUMN cooked_dishes.total_calories IS 'Общая калорийность всего блюда';
COMMENT ON COLUMN cooked_dishes.total_proteins IS 'Общее количество белков во всем блюде';
COMMENT ON COLUMN cooked_dishes.total_fats IS 'Общее количество жиров во всем блюде';
COMMENT ON COLUMN cooked_dishes.total_carbs IS 'Общее количество углеводов во всем блюде';
COMMENT ON COLUMN cooked_dishes.deleted_at IS 'Время мягкого удаления записи';


-- 8. Состав приготовленного блюда (снепшот)
CREATE TABLE cooked_dish_ingredients (
    cooked_dish_id BIGINT NOT NULL,
    ingredient_id INT NOT NULL,
    weight_grams NUMERIC(10, 2) NOT NULL,

    -- Снепшот пищевой ценности на момент приготовления
    calories NUMERIC(8, 2) NOT NULL,
    proteins NUMERIC(8, 2) NOT NULL,
    fats NUMERIC(8, 2) NOT NULL,
    carbs NUMERIC(8, 2) NOT NULL,

    PRIMARY KEY (cooked_dish_id, ingredient_id),

    CONSTRAINT fk_cooked_dish
        FOREIGN KEY(cooked_dish_id)
        REFERENCES cooked_dishes(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_ingredient
        FOREIGN KEY(ingredient_id)
        REFERENCES ingredients(id)
);

COMMENT ON TABLE cooked_dish_ingredients IS 'Снепшот ингредиентов и их КБЖУ на момент приготовления блюда';
COMMENT ON COLUMN cooked_dish_ingredients.cooked_dish_id IS 'Ссылка на приготовленное блюдо';
COMMENT ON COLUMN cooked_dish_ingredients.ingredient_id IS 'Ссылка на ингредиент';
COMMENT ON COLUMN cooked_dish_ingredients.weight_grams IS 'Вес ингредиента в данном блюде';
COMMENT ON COLUMN cooked_dish_ingredients.calories IS 'Калорийность ингредиента на 100г (снепшот)';
COMMENT ON COLUMN cooked_dish_ingredients.proteins IS 'Белки на 100г (снепшот)';
COMMENT ON COLUMN cooked_dish_ingredients.fats IS 'Жиры на 100г (снепшот)';
COMMENT ON COLUMN cooked_dish_ingredients.carbs IS 'Углеводы на 100г (снепшот)';


-- 9. Потребление (факты)
CREATE TABLE consumed (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cooked_dish_id BIGINT NOT NULL,
    consumed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    meal_type VARCHAR(50) NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    weight_grams NUMERIC(10, 2) NOT NULL CHECK (weight_grams > 0),

    -- Пищевая ценность на съеденную порцию
    calories NUMERIC(10, 2) NOT NULL,
    proteins NUMERIC(10, 2) NOT NULL,
    fats NUMERIC(10, 2) NOT NULL,
    carbs NUMERIC(10, 2) NOT NULL,

    CONSTRAINT fk_consumed_dish
        FOREIGN KEY(cooked_dish_id)
        REFERENCES cooked_dishes(id)
);

COMMENT ON TABLE consumed IS 'Факты потребления порций приготовленных блюд';
COMMENT ON COLUMN consumed.id IS 'Уникальный идентификатор факта потребления';
COMMENT ON COLUMN consumed.cooked_dish_id IS 'Ссылка на съеденное блюдо';
COMMENT ON COLUMN consumed.consumed_at IS 'Время потребления';
COMMENT ON COLUMN consumed.meal_type IS 'Тип приема пищи';
COMMENT ON COLUMN consumed.weight_grams IS 'Вес съеденной порции (в граммах)';
COMMENT ON COLUMN consumed.calories IS 'Калорийность съеденной порции';
COMMENT ON COLUMN consumed.proteins IS 'Белки в съеденной порции';
COMMENT ON COLUMN consumed.fats IS 'Жиры в съеденной порции';
COMMENT ON COLUMN consumed.carbs IS 'Углеводы в съеденной порции';

