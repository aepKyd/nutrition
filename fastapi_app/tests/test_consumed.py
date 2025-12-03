from fastapi.testclient import TestClient
from fastapi_app.main import app
import pytest

client = TestClient(app)

# Helper function to create a cooked dish
def create_test_cooked_dish():
    recipe_id = 3 # 'Омлет'
    initial_weight = 500.0
    final_weight = 500.0 # Assume no weight loss for simplicity

    response = client.post(
        "/dishes/",
        json={"recipe_id": recipe_id, "initial_weight": initial_weight, "final_weight": final_weight}
    )
    assert response.status_code == 201
    return response.json()["id"]

def test_create_consumed_item_success():
    cooked_dish_id = create_test_cooked_dish() # Create a fresh cooked dish
    
    response = client.post(
        "/consumed/",
        json={"cooked_dish_id": cooked_dish_id, "meal_type": "breakfast", "weight_grams": 50.0}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["cooked_dish_id"] == cooked_dish_id
    assert data["meal_type"] == "breakfast"
    assert data["weight_grams"] == 50.0
    assert data["calories"] > 0 # Should be calculated by trigger

def test_create_consumed_item_invalid_cooked_dish_id():
    response = client.post(
        "/consumed/",
        json={"cooked_dish_id": 99999, "meal_type": "lunch", "weight_grams": 100.0}
    )
    assert response.status_code == 400
    assert "Database error" in response.json()["detail"]

# Add a test case for when the consumed amount is more than remaining
def test_create_consumed_item_more_than_remaining():
    cooked_dish_id = create_test_cooked_dish() # Create a fresh cooked dish with 500g remaining

    # Consume almost all of it
    client.post(
        "/consumed/",
        json={"cooked_dish_id": cooked_dish_id, "meal_type": "dinner", "weight_grams": 490.0}
    )

    # Now try to consume more than remaining (10g left, try to consume 50g)
    response = client.post(
        "/consumed/",
        json={"cooked_dish_id": cooked_dish_id, "meal_type": "snack", "weight_grams": 50.0}
    )
    assert response.status_code == 201 # Still 201, as trigger adjusts
    data = response.json()
    assert data["cooked_dish_id"] == cooked_dish_id
    assert data["meal_type"] == "snack"
    assert data["weight_grams"] == 10.0 # Should be adjusted to 10.0 (remaining)
    assert data["calories"] > 0


def test_get_update_delete_consumed_item():
    # 1. Create a dish and a consumed item
    cooked_dish_id = create_test_cooked_dish()
    create_response = client.post("/consumed/", json={"cooked_dish_id": cooked_dish_id, "meal_type": "lunch", "weight_grams": 150.0})
    assert create_response.status_code == 201
    new_consumed_id = create_response.json()["id"]

    # 2. Get the created item
    get_response = client.get(f"/consumed/{new_consumed_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == new_consumed_id
    assert get_data["weight_grams"] == 150.0

    # 3. Get list of consumed items
    list_response = client.get("/consumed/")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert isinstance(list_data, list)
    assert any(c["id"] == new_consumed_id for c in list_data)

    # 4. Update the item
    update_data = {"meal_type": "snack", "weight_grams": 100.0}
    update_response = client.put(f"/consumed/{new_consumed_id}", json=update_data)
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["meal_type"] == "snack"
    assert updated_data["weight_grams"] == 100.0

    # 5. Delete the item
    delete_response = client.delete(f"/consumed/{new_consumed_id}")
    assert delete_response.status_code == 204

    # 6. Verify deletion
    get_after_delete_response = client.get(f"/consumed/{new_consumed_id}")
    assert get_after_delete_response.status_code == 404