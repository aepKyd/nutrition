from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import psycopg2
from psycopg2.extras import RealDictCursor
from app.database.session import get_db_connection
from app.schemas.schemas import IngredientSynonym, IngredientSynonymCreate

router = APIRouter()

@router.get("/ingredients/{ingredient_id}/synonyms", response_model=List[IngredientSynonym], tags=["ingredient-synonyms"])
def get_ingredient_synonyms(ingredient_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Retrieve a list of synonyms for a specific ingredient.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT id, ingredient_id, synonym FROM nutrition.ingredient_synonyms WHERE ingredient_id = %s ORDER BY synonym", (ingredient_id,))
        synonyms = cursor.fetchall()
    conn.close()
    return synonyms

@router.post("/ingredients/{ingredient_id}/synonyms", response_model=IngredientSynonym, status_code=status.HTTP_201_CREATED, tags=["ingredient-synonyms"])
def create_ingredient_synonym(ingredient_id: int, synonym: IngredientSynonymCreate, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Create a new synonym for an ingredient.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        try:
            cursor.execute(
                "INSERT INTO nutrition.ingredient_synonyms (ingredient_id, synonym, synonym_normalized) VALUES (%s, %s, '') RETURNING id, ingredient_id, synonym",
                (ingredient_id, synonym.synonym)
            )
            new_synonym = cursor.fetchone()
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")
    conn.close()
    return new_synonym

@router.delete("/ingredients/{ingredient_id}/synonyms/{synonym_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["ingredient-synonyms"])
def delete_ingredient_synonym(ingredient_id: int, synonym_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Delete an ingredient synonym.
    """
    with conn.cursor() as cursor:
        try:
            cursor.execute("DELETE FROM nutrition.ingredient_synonyms WHERE id = %s AND ingredient_id = %s", (synonym_id, ingredient_id))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient synonym not found")
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")
    conn.close()
    return
