import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any
from app.schemas.schemas import IngredientCreate, IngredientUpdate

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
