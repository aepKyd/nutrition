from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import psycopg2
from app.database.session import get_db_connection
from app.schemas.schemas import IngredientCategory, IngredientCategoryCreate, IngredientCategoryUpdate
from app.services import common as services

router = APIRouter()

@router.get("/", response_model=List[IngredientCategory])
def get_ingredient_categories(limit: int = 100, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        return services.get_ingredient_categories(conn, limit)
    except psycopg2.Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

@router.post("/", response_model=IngredientCategory, status_code=status.HTTP_201_CREATED)
def create_ingredient_category(category: IngredientCategoryCreate, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        new_category = services.create_ingredient_category(conn, category)
        conn.commit()
        return new_category
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")

@router.get("/{category_id}", response_model=IngredientCategory)
def get_ingredient_category(category_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    category = services.get_ingredient_category_by_id(conn, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient category not found")
    return category

@router.put("/{category_id}", response_model=IngredientCategory)
def update_ingredient_category(category_id: int, category: IngredientCategoryUpdate, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        updated_category = services.update_ingredient_category(conn, category_id, category)
        if not updated_category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient category not found")
        conn.commit()
        return updated_category
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient_category(category_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        deleted_count = services.delete_ingredient_category(conn, category_id)
        if deleted_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient category not found")
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        if e.pgcode == '23503':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete category that is in use by an ingredient.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")
    return