from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
import psycopg2
from app.database.session import get_db_connection
from app.schemas.schemas import Recipe, RecipeCreate, RecipeNutrition, PopularRecipe
from app.services import recipes as recipe_service

router = APIRouter()

@router.get("/popular", response_model=List[PopularRecipe])
def get_popular_recipes(limit: int = 10, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        return recipe_service.get_popular_recipes(conn, limit)
    except psycopg2.Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

@router.get("/", response_model=List[Recipe])
def get_recipes(search: Optional[str] = None, limit: int = 100, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        return recipe_service.get_recipes(conn, search, limit)
    except psycopg2.Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

@router.post("/", response_model=Recipe, status_code=status.HTTP_201_CREATED)
def create_recipe(recipe: RecipeCreate, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        new_recipe = recipe_service.create_recipe(conn, recipe)
        conn.commit()
        return new_recipe
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")

@router.get("/{recipe_id}", response_model=Recipe)
def get_recipe(recipe_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    return recipe_service.get_recipe_by_id(conn, recipe_id)

@router.get("/{recipe_id}/nutrition", response_model=RecipeNutrition)
def get_recipe_nutrition(recipe_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    return recipe_service.get_recipe_nutrition(conn, recipe_id)

@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(recipe_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        recipe_service.delete_recipe(conn, recipe_id)
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return