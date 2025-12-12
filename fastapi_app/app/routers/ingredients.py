from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import psycopg2
from app.database.session import get_db_connection
from app.schemas.schemas import Ingredient, IngredientCreate, IngredientUpdate
from app.services import ingredients as ingredient_service

router = APIRouter()

@router.get("/search", response_model=List[Ingredient])
def search_ingredients(query: str, limit: int = 10, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        ingredients = ingredient_service.search_ingredients(conn, query, limit)
        return ingredients
    except psycopg2.Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

@router.post("/", response_model=Ingredient, status_code=status.HTTP_201_CREATED)
def create_ingredient(ingredient: IngredientCreate, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        new_ingredient = ingredient_service.create_ingredient(conn, ingredient)
        conn.commit()
        return new_ingredient
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")

@router.get("/{ingredient_id}", response_model=Ingredient)
def get_ingredient(ingredient_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    ingredient = ingredient_service.get_ingredient_by_id(conn, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")
    return ingredient

@router.put("/{ingredient_id}", response_model=Ingredient)
def update_ingredient(ingredient_id: int, ingredient: IngredientUpdate, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        updated_ingredient = ingredient_service.update_ingredient(conn, ingredient_id, ingredient)
        if not updated_ingredient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")
        conn.commit()
        return updated_ingredient
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")

@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(ingredient_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        ingredient_service.delete_ingredient(conn, ingredient_id)
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return