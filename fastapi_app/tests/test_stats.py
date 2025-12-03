from fastapi.testclient import TestClient
from fastapi_app.main import app
from datetime import date
import pytest

client = TestClient(app)

def test_get_daily_summary_success():
    # Assuming there's consumed data for today's date (or a specific test date)
    test_date = date.today().isoformat() # Format as YYYY-MM-DD
    response = client.get(f"/stats/daily_summary?summary_date={test_date}")
    assert response.status_code == 200
    data = response.json()
    assert data["date"] == test_date
    assert "total_nutrition" in data
    assert "meals" in data

def test_get_daily_summary_no_data():
    # Use a date far in the future/past to ensure no data
    test_date = "1900-01-01"
    response = client.get(f"/stats/daily_summary?summary_date={test_date}")
    assert response.status_code == 404
    assert "No summary found for this date." in response.json()["detail"]
