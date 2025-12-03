from fastapi.testclient import TestClient
from fastapi_app.main import app
import pytest
import time

client = TestClient(app)

@pytest.fixture(scope="module")
def test_ingredient():
    unique_name = f"IngredientForSynonymTest {time.time()}"
    new_ingredient_data = {
        "name": unique_name,
        "category_id": 1,
        "calories": 10, "proteins": 1, "fats": 1, "carbs": 1
    }
    response = client.post("/ingredients/", json=new_ingredient_data)
    assert response.status_code == 201
    return response.json()

def test_get_synonyms_for_ingredient(test_ingredient):
    ingredient_id = test_ingredient["id"]
    response = client.get(f"/ingredients/{ingredient_id}/synonyms")
    assert response.status_code == 200
    assert response.json() == []

def test_create_and_delete_synonym(test_ingredient):
    ingredient_id = test_ingredient["id"]
    
    # 1. Create
    new_synonym_data = {"synonym": "Тестовый синоним"}
    create_response = client.post(f"/ingredients/{ingredient_id}/synonyms", json=new_synonym_data)
    assert create_response.status_code == 201
    created_data = create_response.json()
    new_synonym_id = created_data["id"]
    
    assert created_data["synonym"] == new_synonym_data["synonym"]
    assert created_data["ingredient_id"] == ingredient_id

    # 2. Verify creation by getting list
    get_response = client.get(f"/ingredients/{ingredient_id}/synonyms")
    assert get_response.status_code == 200
    synonyms = get_response.json()
    assert len(synonyms) == 1
    assert synonyms[0]["id"] == new_synonym_id

    # 3. Delete
    delete_response = client.delete(f"/ingredients/{ingredient_id}/synonyms/{new_synonym_id}")
    assert delete_response.status_code == 204

    # 4. Verify Deletion
    get_after_delete_response = client.get(f"/ingredients/{ingredient_id}/synonyms")
    assert get_after_delete_response.status_code == 200
    assert get_after_delete_response.json() == []

    # 5. Clean up ingredient
    client.delete(f"/ingredients/{ingredient_id}")
