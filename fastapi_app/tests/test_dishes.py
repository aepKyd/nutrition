from fastapi.testclient import TestClient
from fastapi_app.main import app
import pytest

client = TestClient(app)

def test_create_cooked_dish_success():
    # Assuming recipe_id for 'Омлет' is known (from seed data)
    # In a real scenario, you might fetch this dynamically or use a fixture
    # For now, let's assume recipe_id = 3 for 'Омлет' from init/07_seed_data.sql
    # To make this robust, we should query the DB for recipe_id of 'Омлет'
    # But for a basic test, a hardcoded ID from seed data is acceptable.
    recipe_id = 3 # This corresponds to 'Омлет' in the seed data

    response = client.post(
        "/dishes/",
        json={"recipe_id": recipe_id, "initial_weight": 175.0, "final_weight": 160.0}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["recipe_id"] == recipe_id
    assert data["initial_weight"] == 175.0
    assert data["final_weight"] == 160.0
    assert data["remaining_weight"] == 160.0
    assert data["total_calories"] > 0 # Should be calculated by trigger

def test_create_cooked_dish_invalid_recipe_id():
    response = client.post(
        "/dishes/",
        json={"recipe_id": 99999, "initial_weight": 100.0, "final_weight": 90.0}
    )
    assert response.status_code == 400 # Or 422 if Pydantic validation catches it, but here DB will reject
    assert "Database error" in response.json()["detail"]

def test_get_and_delete_cooked_dish():
    # 1. Create a dish to test with
    recipe_id = 1 # 'Каша овсяная' from seed
    create_response = client.post("/dishes/", json={"recipe_id": recipe_id, "initial_weight": 250, "final_weight": 240})
    assert create_response.status_code == 201
    new_dish_id = create_response.json()["id"]

    # 2. Get the created dish
    get_response = client.get(f"/dishes/{new_dish_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == new_dish_id
    assert get_data["recipe_id"] == recipe_id

    # 3. Get all dishes and check if it's in the list
    list_response = client.get("/dishes/")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert isinstance(list_data, list)
    assert any(d["id"] == new_dish_id for d in list_data)

    # 4. Delete the dish
    delete_response = client.delete(f"/dishes/{new_dish_id}")
    # This might fail if the soft-delete function prevents deletion of non-empty dishes
    # The logic in soft_delete_cooked_dish checks if it was consumed, not if remaining_weight > 0
    # Let's assume it can be deleted for now. If not, this test needs adjustment.
    # The check is `remaining_weight < final_weight`, so if not consumed, it can be deleted.
    assert delete_response.status_code == 204

    # 5. Verify deletion
    get_after_delete_response = client.get(f"/dishes/{new_dish_id}")
    assert get_after_delete_response.status_code == 404

def test_get_remaining_dishes():
    # 1. Create a dish that will have remaining weight
    client.post("/dishes/", json={"recipe_id": 2, "initial_weight": 300, "final_weight": 280})
    
    # 2. Get remaining dishes
    response = client.get("/dishes/remaining")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "cooked_dish_id" in data[0]
    assert "remaining_weight" in data[0]
    assert data[0]["remaining_weight"] > 0
