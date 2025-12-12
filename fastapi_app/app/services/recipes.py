import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
from app.schemas.schemas import RecipeCreate
from app.services.ingredients import get_ingredient_by_id
from app.exceptions import RecipeNotFoundException

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

        if not recipe:
            raise RecipeNotFoundException(f"Recipe with ID {recipe_id} not found.")

        cursor.execute("SELECT ri.ingredient_id, i.name as ingredient_name, ri.weight_grams FROM nutrition.recipe_ingredients ri JOIN nutrition.ingredients i ON ri.ingredient_id = i.id WHERE ri.recipe_id = %s", (recipe["id"],))
        recipe["ingredients"] = cursor.fetchall()
        
        return recipe

def get_recipe_nutrition(conn: psycopg2.extensions.connection, recipe_id: int) -> Dict[str, Any]:
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM nutrition.recipe_nutrition WHERE recipe_id = %s", (recipe_id,))
        result = cursor.fetchone()
        if not result:
             raise RecipeNotFoundException(f"Nutrition data for recipe ID {recipe_id} not found.")
        return result

def delete_recipe(conn: psycopg2.extensions.connection, recipe_id: int):
    with conn.cursor() as cursor:
        cursor.execute("SELECT nutrition.soft_delete_recipe(%s);", (recipe_id,))
