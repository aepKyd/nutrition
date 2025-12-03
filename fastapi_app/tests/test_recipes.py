from fastapi.testclient import TestClient
from fastapi_app.main import app
import pytest

client = TestClient(app)

def test_get_recipes_success():
    response = client.get("/recipes/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "name" in data[0]
    assert "category_name" in data[0]
    assert "ingredients" in data[0]

def test_get_recipes_with_limit():
    response = client.get("/recipes/?limit=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1

def test_create_get_delete_recipe():
    # 1. Create a new recipe
    new_recipe_data = {
        "name": "Тестовый Салат",
        "category_id": 4, # 'Салаты'
        "description": "Простой тестовый салат",
        "instructions": "Смешать все ингредиенты.",
        "ingredients": [
            {"ingredient_id": 22, "weight_grams": 100}, # 'Огурец'
            {"ingredient_id": 23, "weight_grams": 50},  # 'Помидор'
        ],
    }
    create_response = client.post("/recipes/", json=new_recipe_data)
    assert create_response.status_code == 201
    created_data = create_response.json()
    new_recipe_id = created_data["id"]

    assert created_data["name"] == new_recipe_data["name"]
    assert len(created_data["ingredients"]) == 2

    # 2. Get the recipe
    get_response = client.get(f"/recipes/{new_recipe_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == new_recipe_id
    assert get_data["name"] == new_recipe_data["name"]
    assert len(get_data["ingredients"]) == 2
    assert get_data["ingredients"][0]["ingredient_name"] == "Огурец"

    # 3. Delete the recipe
    delete_response = client.delete(f"/recipes/{new_recipe_id}")
    assert delete_response.status_code == 204

    # 4. Verify Deletion
    get_after_delete_response = client.get(f"/recipes/{new_recipe_id}")
    assert get_after_delete_response.status_code == 404

def test_get_popular_recipes():
    response = client.get("/recipes/popular")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "recipe_id" in data[0]
        assert "times_cooked" in data[0]

def test_get_recipe_nutrition():
    # Assuming recipe with ID 1 exists from seed data
    recipe_id = 1
    response = client.get(f"/recipes/{recipe_id}/nutrition")
    assert response.status_code == 200
    data = response.json()
    assert data["recipe_id"] == recipe_id
    assert "total_calories" in data
    assert "total_proteins" in data
    assert "total_fats" in data
    assert "total_carbs" in data
