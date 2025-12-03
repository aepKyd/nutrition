# Nutrition FastAPI Application

This project provides a FastAPI application to interact with the PostgreSQL-based Nutrition API. It exposes RESTful endpoints for searching ingredients, managing recipes, tracking consumed dishes, and viewing daily statistics.

## Setup and Run

1.  **Navigate to the `fastapi_app` directory:**
    ```bash
    cd fastapi_app
    ```

2.  **Create and activate a virtual environment (if you haven't already):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies (if you haven't already):**
    ```bash
    pip install -e .  # Install the project in editable mode
    pip install -r requirements.txt # Assuming a requirements.txt will be generated
    ```
    *Note: If `pip install -e .` fails, ensure your `pip` is updated (`pip install --upgrade pip`).*

4.  **Ensure the PostgreSQL database is running:**
    Navigate to the root `nutrition-api` directory and run:
    ```bash
    docker-compose up -d
    ```

5.  **Run the FastAPI application:**
    ```bash
    uvicorn main:app --reload
    ```
    The application will be available at `http://127.0.0.1:8000`.

## API Documentation

Once the application is running, you can access the interactive API documentation (Swagger UI) at:
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Or the ReDoc documentation at:
[http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Running Tests

To run the API tests, navigate to the root `nutrition-api` directory and execute:
```bash
PYTHONPATH=. fastapi_app/venv/bin/pytest fastapi_app/tests/
```
Ensure the PostgreSQL database is running before executing tests.
