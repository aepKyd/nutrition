from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import psycopg2
from psycopg2.extras import RealDictCursor
from app.database.session import get_db_connection
from app.schemas.schemas import RecipeCategory, RecipeCategoryCreate, RecipeCategoryUpdate

router = APIRouter()

@router.get("/", response_model=List[RecipeCategory])
def get_recipe_categories(limit: int = 100, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Retrieve a list of recipe categories.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT id, name, description FROM nutrition.recipe_categories ORDER BY name LIMIT %s", (limit,))
        categories = cursor.fetchall()
    conn.close()
    return categories

@router.post("/", response_model=RecipeCategory, status_code=status.HTTP_201_CREATED)
def create_recipe_category(category: RecipeCategoryCreate, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Create a new recipe category.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        try:
            cursor.execute(
                "INSERT INTO nutrition.recipe_categories (name, description) VALUES (%s, %s) RETURNING id, name, description",
                (category.name, category.description)
            )
            new_category = cursor.fetchone()
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")
    conn.close()
    return new_category

@router.get("/{category_id}", response_model=RecipeCategory)
def get_recipe_category(category_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Get a single recipe category by ID.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT id, name, description FROM nutrition.recipe_categories WHERE id = %s", (category_id,))
        category = cursor.fetchone()
    conn.close()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe category not found")
    return category

@router.put("/{category_id}", response_model=RecipeCategory)
def update_recipe_category(category_id: int, category: RecipeCategoryUpdate, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Update a recipe category.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        update_data = category.model_dump(exclude_unset=True)
        if not update_data:
            return get_recipe_category(category_id, conn)

        set_query = ", ".join([f"{key} = %s" for key in update_data.keys()])
        values = list(update_data.values())
        values.append(category_id)

        try:
            cursor.execute(
                f"UPDATE nutrition.recipe_categories SET {set_query} WHERE id = %s RETURNING id, name, description",
                values
            )
            updated_category = cursor.fetchone()
            if not updated_category:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe category not found")
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")
    conn.close()
    return updated_category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe_category(category_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Delete a recipe category.
    """
    with conn.cursor() as cursor:
        try:
            cursor.execute("DELETE FROM nutrition.recipe_categories WHERE id = %s", (category_id,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe category not found")
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            # Check for foreign key violation
            if e.pgcode == '23503':
                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete category that is in use by a recipe.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")
    conn.close()
    return
