# ER Диаграмма базы данных

Ниже представлена Entity-Relationship диаграмма для базы данных `nutrition`.

## Mermaid диаграмма

```mermaid
erDiagram
    ingredient_categories {
        SMALLINT id PK
        VARCHAR(100) name
        TEXT description
    }

    recipe_categories {
        SMALLINT id PK
        VARCHAR(100) name
        TEXT description
    }

    ingredients {
        INT id PK
        SMALLINT category_id FK
        VARCHAR(200) name
        NUMERIC calories
        NUMERIC proteins
        NUMERIC fats
        NUMERIC carbs
        TIMESTAMPTZ deleted_at
    }

    ingredient_synonyms {
        INT id PK
        INT ingredient_id FK
        VARCHAR(200) synonym
    }

    recipes {
        INT id PK
        SMALLINT category_id FK
        VARCHAR(255) name
        INT times_cooked
        TIMESTAMPTZ deleted_at
    }

    recipe_ingredients {
        INT recipe_id FK
        INT ingredient_id FK
        NUMERIC weight_grams
    }

    cooked_dishes {
        BIGINT id PK
        INT recipe_id FK
        NUMERIC initial_weight
        NUMERIC final_weight
        NUMERIC remaining_weight
        TIMESTAMPTZ deleted_at
    }

    cooked_dish_ingredients {
        BIGINT cooked_dish_id FK
        INT ingredient_id FK
        NUMERIC weight_grams
    }

    consumed {
        BIGINT id PK
        BIGINT cooked_dish_id FK
        VARCHAR(50) meal_type
        NUMERIC weight_grams
    }

    ingredient_categories ||--o{ ingredients : "содержит"
    recipe_categories ||--o{ recipes : "содержит"
    ingredients ||--o{ ingredient_synonyms : "имеет"
    ingredients ||--o{ recipe_ingredients : "входит в"
    recipes ||--o{ recipe_ingredients : "состоит из"
    recipes ||--o{ cooked_dishes : "готовится по"
    cooked_dishes ||--o{ cooked_dish_ingredients : "состоит из (снепшот)"
    ingredients ||--o{ cooked_dish_ingredients : "входит в (снепшот)"
    cooked_dishes ||--o{ consumed : "потребляется"
```

## Описание таблиц и связей

- **ingredient_categories**: Справочник категорий для ингредиентов (например, "Мясо", "Овощи").
- **recipe_categories**: Справочник категорий для рецептов (например, "Завтраки", "Супы").
- **ingredients**: Основной справочник ингредиентов с их КБЖУ на 100г.
    - Связан с `ingredient_categories` по `category_id`.
- **ingredient_synonyms**: Синонимы для ингредиентов для улучшения поиска.
    - Связан с `ingredients` по `ingredient_id`.
- **recipes**: Рецепты блюд.
    - Связан с `recipe_categories` по `category_id`.
- **recipe_ingredients**: Таблица-связка, показывающая, какие ингредиенты и в каком количестве (в граммах) входят в состав рецепта.
    - Связана с `recipes` и `ingredients`.
- **cooked_dishes**: Таблица фактов. Запись здесь означает, что было приготовлено конкретное блюдо по рецепту.
    - Связана с `recipes`.
- **cooked_dish_ingredients**: Снепшот состава приготовленного блюда. Хранит точный состав и КБЖУ ингредиентов на момент приготовления.
    - Связана с `cooked_dishes` и `ingredients`.
- **consumed**: Таблица фактов. Запись здесь означает, что была съедена порция приготовленного блюда.
    - Связана с `cooked_dishes`.
