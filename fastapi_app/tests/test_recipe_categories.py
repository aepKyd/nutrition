from fastapi.testclient import TestClient
from fastapi_app.main import app
import pytest
import time

client = TestClient(app)

def test_get_recipe_categories():
    response = client.get("/recipe_categories/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]
    assert "name" in data[0]

def test_create_get_update_delete_recipe_category():
    unique_name = f"Тестовая категория рецептов {time.time()}"
    
    # 1. Create
    new_category_data = {
        "name": unique_name,
        "description": "Тестовое описание"
    }
    create_response = client.post("/recipe_categories/", json=new_category_data)
    assert create_response.status_code == 201
    created_data = create_response.json()
    new_category_id = created_data["id"]
    
    assert created_data["name"] == new_category_data["name"]
    assert created_data["description"] == new_category_data["description"]

    # 2. Get
    get_response = client.get(f"/recipe_categories/{new_category_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == new_category_id
    assert get_data["name"] == new_category_data["name"]

    # 3. Update
    update_data = {"name": "Обновленная категория", "description": "Новое описание"}
    update_response = client.put(f"/recipe_categories/{new_category_id}", json=update_data)
    assert update_response.status_code == 200
    updated_category = update_response.json()
    assert updated_category["name"] == update_data["name"]
    assert updated_category["description"] == update_data["description"]

    # 4. Delete
    delete_response = client.delete(f"/recipe_categories/{new_category_id}")
    assert delete_response.status_code == 204

    # 5. Verify Deletion
    get_after_delete_response = client.get(f"/recipe_categories/{new_category_id}")
    assert get_after_delete_response.status_code == 404
