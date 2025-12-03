import os
import requests
from dotenv import load_dotenv
from datetime import date

load_dotenv()

API_URL = os.getenv("NUTRITION_API_URL")

def search_recipes(query: str):
    """Search for recipes in the Nutrition API."""
    try:
        response = requests.get(f"{API_URL}/recipes/", params={"search": query, "limit": 5}, timeout=10)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return []

def get_recipes():
    """Get a list of all recipes."""
    try:
        response = requests.get(f"{API_URL}/recipes/", timeout=10)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return []

def get_remaining_dishes():
    """Get a list of dishes with remaining portions."""
    try:
        response = requests.get(f"{API_URL}/dishes/remaining", timeout=10)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return []

def create_cooked_dish(recipe_id: int, initial_weight: float, final_weight: float):
    """Create a new cooked dish."""
    data = {
        "recipe_id": recipe_id,
        "initial_weight": initial_weight,
        "final_weight": final_weight
    }
    try:
        response = requests.post(f"{API_URL}/dishes/", json=data, timeout=10)
        if response.status_code == 201:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return None

def get_today_summary():
    """Get the daily summary for today."""
    try:
        today = date.today().isoformat()
        response = requests.get(f"{API_URL}/stats/daily_summary", params={"summary_date": today}, timeout=10)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return None

def create_consumed_item(cooked_dish_id: int, weight_grams: float, meal_type: str):
    """Create a new consumed item."""
    data = {
        "cooked_dish_id": cooked_dish_id,
        "weight_grams": weight_grams,
        "meal_type": meal_type
    }
    try:
        response = requests.post(f"{API_URL}/consumed/", json=data, timeout=10)
        if response.status_code == 201:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return None
