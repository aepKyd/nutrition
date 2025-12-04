from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from app.database.session import get_db_connection
from app.schemas.schemas import Recipe, RecipeCreate, RecipeIngredient, RecipeIngredientCreate, RecipeNutrition, PopularRecipe

router = APIRouter()

@router.get("/popular", response_model=List[PopularRecipe])
def get_popular_recipes(limit: int = 10, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Retrieve a list of the most popular recipes.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM nutrition.popular_recipes LIMIT %s", (limit,))
        recipes = cursor.fetchall()
    return recipes


@router.get("/", response_model=List[Recipe])
def get_recipes(search: Optional[str] = None, limit: int = 100, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Retrieve a list of active recipes. Can be filtered by name.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        base_query = """
            SELECT 
                r.id, 
                r.name, 
                rc.name as category_name, 
                r.description, 
                r.instructions, 
                r.times_cooked, 
                r.avg_cooked_weight,
                COALESCE(
                    (
                        SELECT json_agg(
                            json_build_object(
                                'ingredient_id', ri.ingredient_id, 
                                'ingredient_name', i.name, 
                                'weight_grams', ri.weight_grams
                            )
                        )
                        FROM nutrition.recipe_ingredients ri
                        JOIN nutrition.ingredients i ON ri.ingredient_id = i.id
                        WHERE ri.recipe_id = r.id
                    ), 
                    '[]'::json
                ) as ingredients
            FROM nutrition.recipes_active r 
            JOIN nutrition.recipe_categories rc ON r.category_id = rc.id 
        """
        
        if search:
            query = base_query + " WHERE r.name ILIKE %s LIMIT %s"
            cursor.execute(query, (f"%{search}%", limit))
        else:
            query = base_query + " LIMIT %s"
            cursor.execute(query, (limit,))
            
        recipes = cursor.fetchall()
    return recipes

@router.post("/", response_model=Recipe, status_code=status.HTTP_201_CREATED)
def create_recipe(recipe: RecipeCreate, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Create a new recipe.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        try:
            cursor.execute(
                """
                INSERT INTO nutrition.recipes (name, category_id, description, instructions)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """,
                (recipe.name, recipe.category_id, recipe.description, recipe.instructions)
            )
            new_recipe_id = cursor.fetchone()['id']

            for ingredient in recipe.ingredients:
                cursor.execute(
                    """
                    INSERT INTO nutrition.recipe_ingredients (recipe_id, ingredient_id, weight_grams)
                    VALUES (%s, %s, %s);
                    """,
                    (new_recipe_id, ingredient.ingredient_id, ingredient.weight_grams)
                )
            
            conn.commit()

        except psycopg2.Error as e:
            conn.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")

    return get_recipe(new_recipe_id, get_db_connection())

@router.get("/{recipe_id}", response_model=Recipe)
def get_recipe(recipe_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Get a single recipe by ID.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT r.id, r.name, rc.name as category_name, r.description, r.instructions, r.times_cooked, r.avg_cooked_weight FROM nutrition.recipes_active r JOIN nutrition.recipe_categories rc ON r.category_id = rc.id WHERE r.id = %s", (recipe_id,))
        recipe = cursor.fetchone()

        if not recipe:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

        cursor.execute("SELECT ri.ingredient_id, i.name as ingredient_name, ri.weight_grams FROM nutrition.recipe_ingredients ri JOIN nutrition.ingredients i ON ri.ingredient_id = i.id WHERE ri.recipe_id = %s", (recipe["id"],))
        recipe["ingredients"] = cursor.fetchall()
        
    return recipe

@router.get("/{recipe_id}/nutrition", response_model=RecipeNutrition)
def get_recipe_nutrition(recipe_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Get the nutritional information for a single recipe.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM nutrition.recipe_nutrition WHERE recipe_id = %s", (recipe_id,))
        nutrition = cursor.fetchone()
    if not nutrition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    return nutrition

@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(recipe_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Soft-delete a recipe.
    """
    with conn.cursor() as cursor:
        try:
            cursor.execute("SELECT nutrition.soft_delete_recipe(%s);", (recipe_id,))
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return
