from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import psycopg2
from app.database.session import get_db_connection
from app.schemas.schemas import RecipeCategory, RecipeCategoryCreate, RecipeCategoryUpdate
from app.services import recipe_categories as recipe_category_service

router = APIRouter()

@router.get("/", response_model=List[RecipeCategory])
def get_recipe_categories(limit: int = 100, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        return recipe_category_service.get_recipe_categories(conn, limit)
    except psycopg2.Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

@router.post("/", response_model=RecipeCategory, status_code=status.HTTP_201_CREATED)
def create_recipe_category(category: RecipeCategoryCreate, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        new_category = recipe_category_service.create_recipe_category(conn, category)
        conn.commit()
        return new_category
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")

@router.get("/{category_id}", response_model=RecipeCategory)
def get_recipe_category(category_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    category = recipe_category_service.get_recipe_category_by_id(conn, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe category not found")
    return category

@router.put("/{category_id}", response_model=RecipeCategory)
def update_recipe_category(category_id: int, category: RecipeCategoryUpdate, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        updated_category = recipe_category_service.update_recipe_category(conn, category_id, category)
        if not updated_category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe category not found")
        conn.commit()
        return updated_category
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe_category(category_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        deleted_count = recipe_category_service.delete_recipe_category(conn, category_id)
        if deleted_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe category not found")
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        if e.pgcode == '23503':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete category that is in use by a recipe.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")
    return