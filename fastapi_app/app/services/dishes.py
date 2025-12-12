import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any
from app.schemas.schemas import CookedDishCreate

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
