from fastapi.testclient import TestClient
from fastapi_app.main import app
import pytest

client = TestClient(app)

def test_search_ingredients_success():
    response = client.get("/ingredients/search?query=кур")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "name" in data[0]
    assert "category_name" in data[0]
    assert "category_id" in data[0]
    assert "calories" in data[0]

def test_search_ingredients_no_results():
    response = client.get("/ingredients/search?query=nonexistentingredient123")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_search_ingredients_with_limit():
    response = client.get("/ingredients/search?query=масло&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert "Масло" in data[0]["name"]

def test_create_get_update_delete_ingredient():
    import time
    unique_name = f"Тестовый Ингредиент {time.time()}"
    # 1. Create
    new_ingredient_data = {
        "name": unique_name,
        "category_id": 1, # 'Мясо'
        "calories": 100.5,
        "proteins": 10.5,
        "fats": 5.5,
        "carbs": 1.5,
    }
    create_response = client.post("/ingredients/", json=new_ingredient_data)
    assert create_response.status_code == 201
    created_data = create_response.json()
    new_ingredient_id = created_data["id"]
    
    assert created_data["name"] == new_ingredient_data["name"]
    assert created_data["category_id"] == new_ingredient_data["category_id"]

    # 2. Get
    get_response = client.get(f"/ingredients/{new_ingredient_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == new_ingredient_id
    assert get_data["name"] == new_ingredient_data["name"]

    # 3. Update
    updated_name = f"Обновленный Ингредиент {time.time()}"
    update_data = {"name": updated_name, "calories": 150.0}
    update_response = client.put(f"/ingredients/{new_ingredient_id}", json=update_data)
    assert update_response.status_code == 200
    updated_ingredient = update_response.json()
    assert updated_ingredient["name"] == update_data["name"]
    assert updated_ingredient["calories"] == update_data["calories"]

    # 4. Delete
    delete_response = client.delete(f"/ingredients/{new_ingredient_id}")
    assert delete_response.status_code == 204

    # 5. Verify Deletion
    get_after_delete_response = client.get(f"/ingredients/{new_ingredient_id}")
    assert get_after_delete_response.status_code == 404
