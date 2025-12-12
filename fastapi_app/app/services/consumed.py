import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
from datetime import date
from app.schemas.schemas import ConsumedCreate, ConsumedUpdate

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
