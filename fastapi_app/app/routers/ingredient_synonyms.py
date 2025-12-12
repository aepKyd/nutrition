from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import psycopg2
from app.database.session import get_db_connection
from app.schemas.schemas import IngredientSynonym, IngredientSynonymCreate
from app.services import common as services

router = APIRouter()

@router.get("/ingredients/{ingredient_id}/synonyms", response_model=List[IngredientSynonym], tags=["ingredient-synonyms"])
def get_ingredient_synonyms(ingredient_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        return services.get_ingredient_synonyms(conn, ingredient_id)
    except psycopg2.Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

@router.post("/ingredients/{ingredient_id}/synonyms", response_model=IngredientSynonym, status_code=status.HTTP_201_CREATED, tags=["ingredient-synonyms"])
def create_ingredient_synonym(ingredient_id: int, synonym: IngredientSynonymCreate, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        new_synonym = services.create_ingredient_synonym(conn, ingredient_id, synonym)
        conn.commit()
        return new_synonym
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")

@router.delete("/ingredients/{ingredient_id}/synonyms/{synonym_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["ingredient-synonyms"])
def delete_ingredient_synonym(ingredient_id: int, synonym_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        deleted_count = services.delete_ingredient_synonym(conn, ingredient_id, synonym_id)
        if deleted_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient synonym not found")
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")
    return