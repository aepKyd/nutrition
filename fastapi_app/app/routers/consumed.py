from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import date
import psycopg2
from psycopg2.extras import RealDictCursor
from app.database.session import get_db_connection
from app.schemas.schemas import Consumed, ConsumedCreate, ConsumedUpdate

router = APIRouter()

@router.get("/", response_model=List[Consumed])
def get_consumed_items(consumed_date: Optional[date] = None, limit: int = 100, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Retrieve a list of consumed items. Can be filtered by date.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        if consumed_date:
            cursor.execute("SELECT * FROM nutrition.consumed WHERE consumed_at::date = %s ORDER BY consumed_at DESC LIMIT %s", (consumed_date, limit))
        else:
            cursor.execute("SELECT * FROM nutrition.consumed ORDER BY consumed_at DESC LIMIT %s", (limit,))
        items = cursor.fetchall()
    conn.close()
    return items

@router.post("/", response_model=Consumed, status_code=status.HTTP_201_CREATED)
def create_consumed_item(
    consumed_item: ConsumedCreate, conn: psycopg2.extensions.connection = Depends(get_db_connection)
):
    """
    Record a consumed portion of a cooked dish.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        try:
            cursor.execute(
                """
                INSERT INTO nutrition.consumed 
                (cooked_dish_id, meal_type, weight_grams)
                VALUES (%s, %s, %s)
                RETURNING *;
                """,
                (consumed_item.cooked_dish_id, consumed_item.meal_type, consumed_item.weight_grams)
            )
            new_consumed_item = cursor.fetchone()
            conn.commit()

        except psycopg2.Error as e:
            conn.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")
    conn.close()
    return new_consumed_item

@router.get("/{consumed_id}", response_model=Consumed)
def get_consumed_item(consumed_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Get a single consumed item by ID.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM nutrition.consumed WHERE id = %s", (consumed_id,))
        item = cursor.fetchone()
    conn.close()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consumed item not found")
    return item

@router.put("/{consumed_id}", response_model=Consumed)
def update_consumed_item(consumed_id: int, item: ConsumedUpdate, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Update a consumed item.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        update_data = item.model_dump(exclude_unset=True)
        if not update_data:
            return get_consumed_item(consumed_id, conn)

        set_query = ", ".join([f"{key} = %s" for key in update_data.keys()])
        values = list(update_data.values())
        values.append(consumed_id)

        try:
            cursor.execute(
                f"UPDATE nutrition.consumed SET {set_query} WHERE id = %s RETURNING *",
                values
            )
            updated_item = cursor.fetchone()
            if not updated_item:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consumed item not found")
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")
    conn.close()
    return updated_item

@router.delete("/{consumed_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_consumed_item(consumed_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Delete a consumed item. This will also update the remaining weight of the cooked dish.
    """
    with conn.cursor() as cursor:
        try:
            # We need to manually revert the weight change in the cooked_dish
            cursor.execute("SELECT cooked_dish_id, weight_grams FROM nutrition.consumed WHERE id = %s", (consumed_id,))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consumed item not found")
            
            cooked_dish_id, weight_grams = result
            
            cursor.execute("UPDATE nutrition.cooked_dishes SET remaining_weight = remaining_weight + %s WHERE id = %s", (weight_grams, cooked_dish_id))

            cursor.execute("DELETE FROM nutrition.consumed WHERE id = %s", (consumed_id,))
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")
    conn.close()
    return
