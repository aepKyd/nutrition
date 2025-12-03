# Примеры API-запросов

Этот документ содержит примеры SQL-запросов для выполнения основных операций в системе.

## 1. Поиск

### Поиск ингредиентов

Функция `search_ingredients` выполняет многоуровневый поиск по названию, синонимам, с исправлением опечаток.

```sql
-- Поиск ингредиентов, содержащих "кур"
SELECT * FROM nutrition.search_ingredients('кур', 10);

-- Поиск с опечаткой
SELECT * FROM nutrition.search_ingredients('гречкаа', 5);

-- Поиск по синониму "филе"
SELECT * FROM nutrition.search_ingredients('филе', 5);
```

### Просмотр активных рецептов

```sql
SELECT * FROM nutrition.recipes_active;
```

### Просмотр популярных рецептов

```sql
SELECT * FROM nutrition.popular_recipes;
```

## 2. Создание и приготовление

### Создание нового рецепта

```sql
-- 1. Создаем сам рецепт
INSERT INTO nutrition.recipes (category_id, name, description, instructions)
VALUES (
    (SELECT id FROM nutrition.recipe_categories WHERE name = 'Салаты'),
    'Летний салат',
    'Легкий и освежающий салат',
    '1. Нарезать огурцы и помидоры. 2. Добавить масло. 3. Посолить и перемешать.'
)
RETURNING id; -- Получаем id нового рецепта

-- 2. Добавляем ингредиенты в рецепт
INSERT INTO nutrition.recipe_ingredients (recipe_id, ingredient_id, weight_grams) VALUES
    ((SELECT id FROM nutrition.recipes WHERE name = 'Летний салат'), (SELECT id FROM nutrition.ingredients WHERE name = 'Огурец'), 150),
    ((SELECT id FROM nutrition.recipes WHERE name = 'Летний салат'), (SELECT id FROM nutrition.ingredients WHERE name = 'Помидор'), 100),
    ((SELECT id FROM nutrition.recipes WHERE name = 'Летний салат'), (SELECT id FROM nutrition.ingredients WHERE name = 'Масло подсолнечное'), 10);
```

### Приготовление блюда по рецепту

```sql
-- 1. Создаем запись о приготовлении, указывая финальный вес
INSERT INTO nutrition.cooked_dishes (recipe_id, initial_weight, final_weight, remaining_weight, total_calories, total_proteins, total_fats, total_carbs)
VALUES (
    (SELECT id FROM nutrition.recipes WHERE name = 'Гречка с курицей'),
    255, -- 100г гречки + 150г курицы + 5г масла
    250, -- Предположим, вес после варки
    250,
    0, 0, 0, 0 -- КБЖУ будет рассчитан триггером
) RETURNING id; -- Получаем id приготовленного блюда

-- 2. Заполняем снепшот ингредиентов (это действие должен выполнять ваш бэкенд-клиент)
INSERT INTO nutrition.cooked_dish_ingredients (cooked_dish_id, ingredient_id, weight_grams, calories, proteins, fats, carbs)
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
    WHERE ri.recipe_id = (SELECT id FROM recipes WHERE name = 'Гречка с курицей');
```
*Примечание: Триггер `trg_recalculate_dish_nutrition` автоматически рассчитает и обновит КБЖУ для `cooked_dishes` после вставки данных в `cooked_dish_ingredients`.*

## 3. Учет потребления

### Потребление порции блюда

```sql
-- Съедаем 150г приготовленной гречки с курицей
-- cooked_dish_id - это id из таблицы cooked_dishes
INSERT INTO nutrition.consumed (cooked_dish_id, meal_type, weight_grams)
VALUES (1, 'lunch', 150);
```
*Примечание: Триггер `trg_calculate_consumed_nutrition` автоматически рассчитает КБЖУ для порции и обновит остаток в `cooked_dishes`.*

## 4. Статистика

### Получение дневной статистики

Функция `get_daily_summary` возвращает JSON-объект с полной статистикой за указанный день.

```sql
SELECT nutrition.get_daily_summary('2025-11-24');
```
Пример ответа:
```json
{
  "date": "2025-11-24",
  "total_nutrition": {
    "fats": 11.76,
    "carbs": 2.02,
    "calories": 158.06,
    "proteins": 10.48
  },
  "meals": [
    {
      "fats": 11.76,
      "carbs": 2.02,
      "calories": 158.06,
      "proteins": 10.48,
      "meal_type": "breakfast",
      "portions_count": 1
    }
  ]
}
```

### Просмотр оставшихся блюд

```sql
SELECT * FROM nutrition.remaining_dishes;
```

## 5. Мягкое удаление

### Удаление ингредиента

```sql
-- Попытка удалить ингредиент, который не используется
SELECT nutrition.soft_delete_ingredient((SELECT id FROM ingredients WHERE name = 'Удаляемый ингредиент'));
```
*Примечание: Функция вернет ошибку, если ингредиент используется в рецептах.*

### Удаление рецепта

```sql
-- Попытка удалить рецепт, который не используется в приготовленных блюдах
SELECT nutrition.soft_delete_recipe((SELECT id FROM recipes WHERE name = 'Летний салат'));
```
*Примечание: Функция вернет ошибку, если по рецепту есть активные (не удаленные) приготовленные блюда.*
