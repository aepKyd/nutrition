import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
from datetime import date
from app.schemas.schemas import IngredientCreate, IngredientUpdate, RecipeCategoryCreate, RecipeCategoryUpdate, IngredientCategoryCreate, IngredientCategoryUpdate, IngredientSynonymCreate, CookedDishCreate, ConsumedCreate, ConsumedUpdate, RecipeCreate

# Ingredient Service

def search_ingredients(conn: psycopg2.extensions.connection, query: str, limit: int) -> List[Dict[str, Any]]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            """
            SELECT i.id, i.name, i.category_id, ic.name as category_name, i.calories, i.proteins, i.fats, i.carbs, s.search_score 
            FROM nutrition.search_ingredients(%s, %s) s 
            JOIN nutrition.ingredients i ON s.id = i.id 
            JOIN nutrition.ingredient_categories ic ON i.category_id = ic.id
            """, 
            (query, limit)
        )
        return cursor.fetchall()

def create_ingredient(conn: psycopg2.extensions.connection, ingredient: IngredientCreate) -> Dict[str, Any]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            """
            INSERT INTO nutrition.ingredients (name, category_id, calories, proteins, fats, carbs, name_normalized)
            VALUES (%s, %s, %s, %s, %s, %s, '')
            RETURNING id;
            """,
            (ingredient.name, ingredient.category_id, ingredient.calories, ingredient.proteins, ingredient.fats, ingredient.carbs)
        )
        new_ingredient_id = cursor.fetchone()['id']
        
        cursor.execute(
            """
            SELECT i.id, i.name, i.category_id, ic.name as category_name, i.calories, i.proteins, i.fats, i.carbs 
            FROM nutrition.ingredients i 
            JOIN nutrition.ingredient_categories ic ON i.category_id = ic.id 
            WHERE i.id = %s
            """, 
            (new_ingredient_id,)
        )
        return cursor.fetchone()

def get_ingredient_by_id(conn: psycopg2.extensions.connection, ingredient_id: int) -> Dict[str, Any]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            """
            SELECT i.id, i.name, i.category_id, ic.name as category_name, i.calories, i.proteins, i.fats, i.carbs 
            FROM nutrition.ingredients_active i 
            JOIN nutrition.ingredient_categories ic ON i.category_id = ic.id 
            WHERE i.id = %s
            """, 
            (ingredient_id,)
        )
        return cursor.fetchone()

def update_ingredient(conn: psycopg2.extensions.connection, ingredient_id: int, ingredient: IngredientUpdate) -> Dict[str, Any]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM nutrition.ingredients WHERE id = %s", (ingredient_id,))
        if not cursor.fetchone():
            return None

        update_data = ingredient.model_dump(exclude_unset=True)
        if not update_data:
            return get_ingredient_by_id(conn, ingredient_id)

        set_query = ", ".join([f"{key} = %s" for key in update_data.keys()])
        values = list(update_data.values())
        values.append(ingredient_id)

        query = f"UPDATE nutrition.ingredients SET {set_query}, updated_at=NOW() WHERE id = %s"
        cursor.execute(query, values)
        
        return get_ingredient_by_id(conn, ingredient_id)

def delete_ingredient(conn: psycopg2.extensions.connection, ingredient_id: int):
    with conn.cursor() as cursor:
        cursor.execute("SELECT nutrition.soft_delete_ingredient(%s);", (ingredient_id,))

# Recipe Service

def get_popular_recipes(conn: psycopg2.extensions.connection, limit: int) -> List[Dict[str, Any]]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM nutrition.popular_recipes LIMIT %s", (limit,))
        return cursor.fetchall()

def get_recipes(conn: psycopg2.extensions.connection, search: Optional[str], limit: int) -> List[Dict[str, Any]]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        base_query = """
            SELECT 
                r.id, 
                r.name, 
                rc.name as category_name, 
                r.description, 
                r.instructions, 
                r.times_cooked, 
                r.avg_cooked_weight,
                COALESCE(
                    (
                        SELECT json_agg(
                            json_build_object(
                                'ingredient_id', ri.ingredient_id, 
                                'ingredient_name', i.name, 
                                'weight_grams', ri.weight_grams
                            )
                        )
                        FROM nutrition.recipe_ingredients ri
                        JOIN nutrition.ingredients i ON ri.ingredient_id = i.id
                        WHERE ri.recipe_id = r.id
                    ), 
                    '[]'::json
                ) as ingredients
            FROM nutrition.recipes_active r 
            JOIN nutrition.recipe_categories rc ON r.category_id = rc.id 
        """
        
        if search:
            query = base_query + " WHERE r.name ILIKE %s LIMIT %s"
            cursor.execute(query, (f"%{search}%", limit))
        else:
            query = base_query + " LIMIT %s"
            cursor.execute(query, (limit,))
            
        return cursor.fetchall()

def create_recipe(conn: psycopg2.extensions.connection, recipe: RecipeCreate) -> Dict[str, Any]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            """
            INSERT INTO nutrition.recipes (name, category_id, description, instructions)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
            """,
            (recipe.name, recipe.category_id, recipe.description, recipe.instructions)
        )
        new_recipe_id = cursor.fetchone()['id']

        for ingredient in recipe.ingredients:
            cursor.execute(
                """
                INSERT INTO nutrition.recipe_ingredients (recipe_id, ingredient_id, weight_grams)
                VALUES (%s, %s, %s);
                """,
                (new_recipe_id, ingredient.ingredient_id, ingredient.weight_grams)
            )
        
        return get_recipe_by_id(conn, new_recipe_id)

def get_recipe_by_id(conn: psycopg2.extensions.connection, recipe_id: int) -> Dict[str, Any]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT r.id, r.name, rc.name as category_name, r.description, r.instructions, r.times_cooked, r.avg_cooked_weight FROM nutrition.recipes_active r JOIN nutrition.recipe_categories rc ON r.category_id = rc.id WHERE r.id = %s", (recipe_id,))
        recipe = cursor.fetchone()

        if recipe:
            cursor.execute("SELECT ri.ingredient_id, i.name as ingredient_name, ri.weight_grams FROM nutrition.recipe_ingredients ri JOIN nutrition.ingredients i ON ri.ingredient_id = i.id WHERE ri.recipe_id = %s", (recipe["id"],))
            recipe["ingredients"] = cursor.fetchall()
        
        return recipe

def get_recipe_nutrition(conn: psycopg2.extensions.connection, recipe_id: int) -> Dict[str, Any]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM nutrition.recipe_nutrition WHERE recipe_id = %s", (recipe_id,))
        return cursor.fetchone()

def delete_recipe(conn: psycopg2.extensions.connection, recipe_id: int):
    with conn.cursor() as cursor:
        cursor.execute("SELECT nutrition.soft_delete_recipe(%s);", (recipe_id,))

# Dish Service

def get_remaining_dishes(conn: psycopg2.extensions.connection, limit: int) -> List[Dict[str, Any]]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM nutrition.remaining_dishes ORDER BY cooked_at DESC LIMIT %s", (limit,))
        return cursor.fetchall()

def get_cooked_dishes(conn: psycopg2.extensions.connection, limit: int) -> List[Dict[str, Any]]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM nutrition.cooked_dishes_active ORDER BY cooked_at DESC LIMIT %s", (limit,))
        return cursor.fetchall()

def create_cooked_dish(conn: psycopg2.extensions.connection, dish: CookedDishCreate) -> Dict[str, Any]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            """
            INSERT INTO nutrition.cooked_dishes 
            (recipe_id, initial_weight, final_weight, remaining_weight, total_calories, total_proteins, total_fats, total_carbs)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (dish.recipe_id, dish.initial_weight, dish.final_weight, dish.final_weight, 0, 0, 0, 0)
        )
        cooked_dish_id = cursor.fetchone()['id']
        
        cursor.execute(
            """
            INSERT INTO nutrition.cooked_dish_ingredients 
            (cooked_dish_id, ingredient_id, weight_grams, calories, proteins, fats, carbs)
            SELECT %s, ri.ingredient_id, ri.weight_grams, i.calories, i.proteins, i.fats, i.carbs
            FROM nutrition.recipe_ingredients ri
            JOIN nutrition.ingredients i ON ri.ingredient_id = i.id
            WHERE ri.recipe_id = %s;
            """,
            (cooked_dish_id, dish.recipe_id)
        )
        
        cursor.execute("SELECT * FROM nutrition.cooked_dishes_active WHERE id = %s", (cooked_dish_id,))
        return cursor.fetchone()

def get_cooked_dish_by_id(conn: psycopg2.extensions.connection, dish_id: int) -> Dict[str, Any]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM nutrition.cooked_dishes_active WHERE id = %s", (dish_id,))
        return cursor.fetchone()

def delete_cooked_dish(conn: psycopg2.extensions.connection, dish_id: int):
    with conn.cursor() as cursor:
        cursor.execute("SELECT nutrition.soft_delete_cooked_dish(%s);", (dish_id,))

# Consumed Service

def get_consumed_items(conn: psycopg2.extensions.connection, consumed_date: Optional[date], limit: int) -> List[Dict[str, Any]]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        if consumed_date:
            cursor.execute("SELECT * FROM nutrition.consumed WHERE consumed_at::date = %s ORDER BY consumed_at DESC LIMIT %s", (consumed_date, limit))
        else:
            cursor.execute("SELECT * FROM nutrition.consumed ORDER BY consumed_at DESC LIMIT %s", (limit,))
        return cursor.fetchall()

def create_consumed_item(conn: psycopg2.extensions.connection, consumed_item: ConsumedCreate) -> Dict[str, Any]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            """
            INSERT INTO nutrition.consumed 
            (cooked_dish_id, meal_type, weight_grams)
            VALUES (%s, %s, %s)
            RETURNING *;
            """,
            (consumed_item.cooked_dish_id, consumed_item.meal_type, consumed_item.weight_grams)
        )
        return cursor.fetchone()

def get_consumed_item_by_id(conn: psycopg2.extensions.connection, consumed_id: int) -> Dict[str, Any]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM nutrition.consumed WHERE id = %s", (consumed_id,))
        return cursor.fetchone()

def update_consumed_item(conn: psycopg2.extensions.connection, consumed_id: int, item: ConsumedUpdate) -> Dict[str, Any]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        update_data = item.model_dump(exclude_unset=True)
        if not update_data:
            return get_consumed_item_by_id(conn, consumed_id)

        set_query = ", ".join([f"{key} = %s" for key in update_data.keys()])
        values = list(update_data.values())
        values.append(consumed_id)

        cursor.execute(
            f"UPDATE nutrition.consumed SET {set_query} WHERE id = %s RETURNING *",
            values
        )
        return cursor.fetchone()

def delete_consumed_item(conn: psycopg2.extensions.connection, consumed_id: int) -> int:
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM nutrition.consumed WHERE id = %s", (consumed_id,))
        return cursor.rowcount

# Stats Service

def get_daily_summary(conn: psycopg2.extensions.connection, summary_date: date) -> Dict[str, Any]:
    with conn.cursor() as cursor:
        cursor.execute("SELECT nutrition.get_daily_summary(%s);", (summary_date,))
        result = cursor.fetchone()
        if result and result[0]:
            return result[0]
        return None

# Ingredient Category Service

def get_ingredient_categories(conn: psycopg2.extensions.connection, limit: int) -> List[Dict[str, Any]]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT id, name, description FROM nutrition.ingredient_categories ORDER BY name LIMIT %s", (limit,))
        return cursor.fetchall()

def create_ingredient_category(conn: psycopg2.extensions.connection, category: IngredientCategoryCreate) -> Dict[str, Any]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            "INSERT INTO nutrition.ingredient_categories (name, description) VALUES (%s, %s) RETURNING id, name, description",
            (category.name, category.description)
        )
        return cursor.fetchone()

def get_ingredient_category_by_id(conn: psycopg2.extensions.connection, category_id: int) -> Dict[str, Any]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT id, name, description FROM nutrition.ingredient_categories WHERE id = %s", (category_id,))
        return cursor.fetchone()

def update_ingredient_category(conn: psycopg2.extensions.connection, category_id: int, category: IngredientCategoryUpdate) -> Dict[str, Any]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        update_data = category.model_dump(exclude_unset=True)
        if not update_data:
            return get_ingredient_category_by_id(conn, category_id)

        set_query = ", ".join([f"{key} = %s" for key in update_data.keys()])
        values = list(update_data.values())
        values.append(category_id)

        cursor.execute(
            f"UPDATE nutrition.ingredient_categories SET {set_query} WHERE id = %s RETURNING id, name, description",
            values
        )
        return cursor.fetchone()

def delete_ingredient_category(conn: psycopg2.extensions.connection, category_id: int) -> int:
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM nutrition.ingredient_categories WHERE id = %s", (category_id,))
        return cursor.rowcount

# Recipe Category Service

def get_recipe_categories(conn: psycopg2.extensions.connection, limit: int) -> List[Dict[str, Any]]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT id, name, description FROM nutrition.recipe_categories ORDER BY name LIMIT %s", (limit,))
        return cursor.fetchall()

def create_recipe_category(conn: psycopg2.extensions.connection, category: RecipeCategoryCreate) -> Dict[str, Any]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            "INSERT INTO nutrition.recipe_categories (name, description) VALUES (%s, %s) RETURNING id, name, description",
            (category.name, category.description)
        )
        return cursor.fetchone()

def get_recipe_category_by_id(conn: psycopg2.extensions.connection, category_id: int) -> Dict[str, Any]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT id, name, description FROM nutrition.recipe_categories WHERE id = %s", (category_id,))
        return cursor.fetchone()

def update_recipe_category(conn: psycopg2.extensions.connection, category_id: int, category: RecipeCategoryUpdate) -> Dict[str, Any]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        update_data = category.model_dump(exclude_unset=True)
        if not update_data:
            return get_recipe_category_by_id(conn, category_id)

        set_query = ", ".join([f"{key} = %s" for key in update_data.keys()])
        values = list(update_data.values())
        values.append(category_id)

        cursor.execute(
            f"UPDATE nutrition.recipe_categories SET {set_query} WHERE id = %s RETURNING id, name, description",
            values
        )
        return cursor.fetchone()

def delete_recipe_category(conn: psycopg2.extensions.connection, category_id: int) -> int:
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM nutrition.recipe_categories WHERE id = %s", (category_id,))
        return cursor.rowcount

# Ingredient Synonym Service

def get_ingredient_synonyms(conn: psycopg2.extensions.connection, ingredient_id: int) -> List[Dict[str, Any]]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT id, ingredient_id, synonym FROM nutrition.ingredient_synonyms WHERE ingredient_id = %s ORDER BY synonym", (ingredient_id,))
        return cursor.fetchall()

def create_ingredient_synonym(conn: psycopg2.extensions.connection, ingredient_id: int, synonym: IngredientSynonymCreate) -> Dict[str, Any]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            "INSERT INTO nutrition.ingredient_synonyms (ingredient_id, synonym, synonym_normalized) VALUES (%s, %s, '') RETURNING id, ingredient_id, synonym",
            (ingredient_id, synonym.synonym)
        )
        return cursor.fetchone()

def delete_ingredient_synonym(conn: psycopg2.extensions.connection, ingredient_id: int, synonym_id: int) -> int:
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM nutrition.ingredient_synonyms WHERE id = %s AND ingredient_id = %s", (synonym_id, ingredient_id))
        return cursor.rowcount

