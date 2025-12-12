from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from app.database.session import get_db_connection
from app.schemas.schemas import CookedDish, CookedDishCreate, RemainingDish

router = APIRouter()

@router.get("/remaining", response_model=List[RemainingDish])
def get_remaining_dishes(limit: int = 100, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Retrieve a list of cooked dishes with remaining weight.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM nutrition.remaining_dishes ORDER BY cooked_at DESC LIMIT %s", (limit,))
        dishes = cursor.fetchall()
    return dishes


@router.get("/", response_model=List[CookedDish])
def get_cooked_dishes(limit: int = 100, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Retrieve a list of active cooked dishes.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM nutrition.cooked_dishes_active ORDER BY cooked_at DESC LIMIT %s", (limit,))
        dishes = cursor.fetchall()
    return dishes

@router.post("/", response_model=CookedDish, status_code=status.HTTP_201_CREATED)
def create_cooked_dish(
    dish: CookedDishCreate, conn: psycopg2.extensions.connection = Depends(get_db_connection)
):
    """
    Create a new cooked dish from a recipe.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        try:
            # Insert into cooked_dishes
            cursor.execute(
                """
                INSERT INTO nutrition.cooked_dishes 
                (recipe_id, initial_weight, final_weight, remaining_weight, total_calories, total_proteins, total_fats, total_carbs)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (dish.recipe_id, dish.initial_weight, dish.final_weight, dish.final_weight, 0, 0, 0, 0) # KBHU will be calculated by trigger
            )
            cooked_dish_id = cursor.fetchone()['id']
            
            # Get ingredients from the recipe and insert into cooked_dish_ingredients
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
            conn.commit()

            # Fetch the complete cooked dish data
            cursor.execute("SELECT * FROM nutrition.cooked_dishes_active WHERE id = %s", (cooked_dish_id,))
            new_dish = cursor.fetchone()

        except psycopg2.Error as e:
            conn.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")
    return new_dish

@router.get("/{dish_id}", response_model=CookedDish)
def get_cooked_dish(dish_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Get a single cooked dish by ID.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM nutrition.cooked_dishes_active WHERE id = %s", (dish_id,))
        dish = cursor.fetchone()
    if not dish:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cooked dish not found")
    return dish

@router.delete("/{dish_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cooked_dish(dish_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Soft-delete a cooked dish.
    """
    with conn.cursor() as cursor:
        try:
            cursor.execute("SELECT nutrition.soft_delete_cooked_dish(%s);", (dish_id,))
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return
