from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class Ingredient(BaseModel):
    id: int
    name: str
    category_id: int
    category_name: str
    calories: float
    proteins: float
    fats: float
    carbs: float
    search_score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class IngredientCreate(BaseModel):
    name: str
    category_id: int
    calories: float
    proteins: float
    fats: float
    carbs: float

class IngredientUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    calories: Optional[float] = None
    proteins: Optional[float] = None
    fats: Optional[float] = None
    carbs: Optional[float] = None


class Recipe(BaseModel):
    id: int
    name: str
    category_name: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    times_cooked: int
    avg_cooked_weight: Optional[float] = None
    ingredients: Optional[List['RecipeIngredient']] = []

    model_config = ConfigDict(from_attributes=True)

class RecipeIngredient(BaseModel):
    ingredient_id: int
    ingredient_name: str
    weight_grams: float

    model_config = ConfigDict(from_attributes=True)
        
class RecipeIngredientCreate(BaseModel):
    ingredient_id: int
    weight_grams: float

class RecipeCreate(BaseModel):
    name: str
    category_id: int
    description: Optional[str] = None
    instructions: Optional[str] = None
    ingredients: List[RecipeIngredientCreate]


class CookedDishCreate(BaseModel):
    recipe_id: int
    initial_weight: float
    final_weight: float
    # total_calories, total_proteins, total_fats, total_carbs will be calculated by trigger

from datetime import datetime

class CookedDish(BaseModel):
    id: int
    recipe_id: int
    cooked_at: datetime
    initial_weight: float
    final_weight: float
    remaining_weight: float
    total_calories: float
    total_proteins: float
    total_fats: float
    total_carbs: float
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ConsumedCreate(BaseModel):
    cooked_dish_id: int
    meal_type: str
    weight_grams: float

class Consumed(BaseModel):
    id: int
    cooked_dish_id: int
    consumed_at: datetime
    meal_type: str
    weight_grams: float
    calories: float
    proteins: float
    fats: float
    carbs: float

    model_config = ConfigDict(from_attributes=True)

class TotalNutritionSummary(BaseModel):
    calories: float
    proteins: float
    fats: float
    carbs: float

class MealSummary(TotalNutritionSummary):
    meal_type: str
    portions_count: int

class DailySummary(BaseModel):
    date: str
    total_nutrition: TotalNutritionSummary
    meals: Optional[List[MealSummary]] = None

class IngredientCategory(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class IngredientCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class IngredientCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class RecipeCategory(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class RecipeCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class RecipeCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class IngredientSynonym(BaseModel):
    id: int
    ingredient_id: int
    synonym: str

    model_config = ConfigDict(from_attributes=True)

class IngredientSynonymCreate(BaseModel):
    synonym: str

class ConsumedUpdate(BaseModel):
    meal_type: Optional[str] = None
    weight_grams: Optional[float] = None

class RecipeNutrition(BaseModel):
    recipe_id: int
    recipe_name: str
    total_calories: float
    total_proteins: float
    total_fats: float
    total_carbs: float

    model_config = ConfigDict(from_attributes=True)

class RemainingDish(BaseModel):
    cooked_dish_id: int
    recipe_name: str
    cooked_at: datetime
    remaining_weight: float
    calories_per_100g: float
    proteins_per_100g: float
    fats_per_100g: float
    carbs_per_100g: float

    model_config = ConfigDict(from_attributes=True)

class PopularRecipe(BaseModel):
    recipe_id: int
    recipe_name: str
    recipe_description: Optional[str] = None
    times_cooked: int
    avg_cooked_weight: Optional[float] = None
    total_cooked_dishes_count: int

    model_config = ConfigDict(from_attributes=True)

