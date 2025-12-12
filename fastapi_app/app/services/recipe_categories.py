import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any
from app.schemas.schemas import RecipeCategoryCreate, RecipeCategoryUpdate

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
