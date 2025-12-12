import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any
from app.schemas.schemas import IngredientSynonymCreate

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
