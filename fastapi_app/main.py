from fastapi import FastAPI
from app.routers import ingredients, recipes, dishes, consumed, stats, ingredient_categories, recipe_categories, ingredient_synonyms

app = FastAPI(
    title="Nutrition API",
    description="A FastAPI application to interact with the Nutrition database.",
    version="1.0.0",
)

app.include_router(ingredient_categories.router, prefix="/ingredient_categories", tags=["ingredient-categories"])
app.include_router(recipe_categories.router, prefix="/recipe_categories", tags=["recipe-categories"])
app.include_router(ingredients.router, prefix="/ingredients", tags=["ingredients"])
app.include_router(ingredient_synonyms.router) # No prefix, as it's defined in the router
app.include_router(recipes.router, prefix="/recipes", tags=["recipes"])
app.include_router(dishes.router, prefix="/dishes", tags=["dishes"])
app.include_router(consumed.router, prefix="/consumed", tags=["consumed"])
app.include_router(stats.router, prefix="/stats", tags=["statistics"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Nutrition API"}
