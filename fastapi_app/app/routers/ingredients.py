from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from app.database.session import get_db_connection
from app.schemas.schemas import Ingredient, IngredientCreate, IngredientUpdate

router = APIRouter()

@router.get("/search", response_model=List[Ingredient])
def search_ingredients(query: str, limit: int = 10, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Search for ingredients by query.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT i.id, i.name, i.category_id, ic.name as category_name, i.calories, i.proteins, i.fats, i.carbs, s.search_score FROM nutrition.search_ingredients(%s, %s) s JOIN nutrition.ingredients i ON s.id = i.id JOIN nutrition.ingredient_categories ic ON i.category_id = ic.id", (query, limit))
        ingredients = cursor.fetchall()
    conn.close()
    return ingredients

@router.post("/", response_model=Ingredient, status_code=status.HTTP_201_CREATED)
def create_ingredient(ingredient: IngredientCreate, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Create a new ingredient.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        try:
            cursor.execute(
                """
                INSERT INTO nutrition.ingredients (name, category_id, calories, proteins, fats, carbs, name_normalized)
                VALUES (%s, %s, %s, %s, %s, %s, '')
                RETURNING id;
                """,
                (ingredient.name, ingredient.category_id, ingredient.calories, ingredient.proteins, ingredient.fats, ingredient.carbs)
            )
            new_ingredient_id = cursor.fetchone()['id']
            conn.commit()
            
            cursor.execute("SELECT i.id, i.name, i.category_id, ic.name as category_name, i.calories, i.proteins, i.fats, i.carbs FROM nutrition.ingredients i JOIN nutrition.ingredient_categories ic ON i.category_id = ic.id WHERE i.id = %s", (new_ingredient_id,))
            new_ingredient = cursor.fetchone()

        except psycopg2.Error as e:
            conn.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")
    conn.close()
    return new_ingredient

@router.get("/{ingredient_id}", response_model=Ingredient)
def get_ingredient(ingredient_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Get a single ingredient by ID.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT i.id, i.name, i.category_id, ic.name as category_name, i.calories, i.proteins, i.fats, i.carbs FROM nutrition.ingredients_active i JOIN nutrition.ingredient_categories ic ON i.category_id = ic.id WHERE i.id = %s", (ingredient_id,))
        ingredient = cursor.fetchone()
    conn.close()
    if not ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")
    return ingredient

@router.put("/{ingredient_id}", response_model=Ingredient)
def update_ingredient(ingredient_id: int, ingredient: IngredientUpdate, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Update an ingredient.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        # Fetch current ingredient to see what needs updating
        cursor.execute("SELECT * FROM nutrition.ingredients WHERE id = %s", (ingredient_id,))
        current_ingredient = cursor.fetchone()
        if not current_ingredient:
            conn.close()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")

        update_data = ingredient.model_dump(exclude_unset=True)
        if not update_data:
            conn.close()
            return get_ingredient(ingredient_id, get_db_connection())

        # Build the SET part of the SQL query dynamically
        set_query = ", ".join([f"{key} = %s" for key in update_data.keys()])
        values = list(update_data.values())
        values.append(ingredient_id)

        try:
            query = f"UPDATE nutrition.ingredients SET {set_query}, updated_at=NOW() WHERE id = %s"
            with open("update_query.log", "w") as f:
                f.write(f"Query: {query}\n")
                f.write(f"Values: {values}\n")
            cursor.execute(query, values)
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")
            
    conn.close()
    return get_ingredient(ingredient_id, get_db_connection())


@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(ingredient_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Soft-delete an ingredient.
    """
    with conn.cursor() as cursor:
        try:
            cursor.execute("SELECT nutrition.soft_delete_ingredient(%s);", (ingredient_id,))
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    conn.close()
    return

