# План реализации FastAPI приложения

**Цель:** Создать API-сервис на FastAPI для взаимодействия с существующей базой данных `nutrition`.

---

## Этап 1: Настройка окружения (1-2 часа)

**Цель:** Подготовить окружение для разработки FastAPI приложения.

**Задачи:**
1.  **Создать виртуальное окружение:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
2.  **Установить зависимости:**
    ```bash
    pip install fastapi uvicorn psycopg2-binary pydantic python-dotenv
    ```
3.  **Создать структуру проекта:**
    ```bash
    touch main.py .env
    mkdir -p app/{database,models,routers,schemas,crud}
    touch app/__init__.py
    touch app/database/__init__.py app/database/session.py
    touch app/models/__init__.py app/models/models.py
    touch app/routers/__init__.py app/routers/ingredients.py app/routers/recipes.py
    touch app/schemas/__init__.py app/schemas/schemas.py
    touch app/crud/__init__.py app/crud/crud.py
    ```

## Этап 2: Подключение к базе данных (1-2 часа)

**Цель:** Настроить подключение к PostgreSQL и определить модели данных.

**Задачи:**
1.  **Настроить `.env`:**
    - Скопировать переменные из корневого `.env` файла.
2.  **Реализовать подключение к БД (`app/database/session.py`):**
    - Настроить подключение к PostgreSQL с использованием `psycopg2`.
3.  **Определить Pydantic модели (`app/schemas/schemas.py`):**
    - Создать Pydantic-схемы для всех основных сущностей (Ingredient, Recipe, Consumed и т.д.), которые будут использоваться для валидации данных в API.

## Этап 3: Реализация эндпоинтов (3-5 часов)

**Цель:** Создать API-эндпоинты для всех основных операций.

**Задачи (в `app/routers/`):**

1.  **`ingredients.py`:**
    - `GET /ingredients/search`: Поиск ингредиентов. Будет вызывать функцию `nutrition.search_ingredients` в БД.
2.  **`recipes.py`:**
    - `GET /recipes`: Получение списка активных рецептов из `nutrition.recipes_active`.
    - `POST /recipes`: Создание нового рецепта.
3.  **`dishes.py` (новый файл):**
    - `POST /dishes`: Приготовление блюда.
4.  **`consumed.py` (новый файл):**
    - `POST /consumed`: Учет потребления.
5.  **`stats.py` (новый файл):**
    - `GET /stats/daily_summary`: Получение дневной статистики.

## Этап 4: Тестирование API (2-3 часа)

**Цель:** Проверить работоспособность API.

**Задачи:**
1.  **Установить `pytest` и `httpx`:**
    ```bash
    pip install pytest httpx
    ```
2.  **Написать тесты:**
    - Создать директорию `tests/`.
    - Написать тесты для каждого эндпоинта, проверяя корректность ответов и кодов состояния.

## Этап 5: Документация API (1 час)

**Цель:** Обеспечить понятную документацию для API.

**Задачи:**
1.  **Добавить описание в FastAPI:**
    - Использовать `title`, `description`, `summary` и `tags` в роутерах FastAPI для автоматической генерации документации OpenAPI (Swagger/ReDoc).
2.  **Обновить `README.md`:**
    - Добавить инструкции по запуску FastAPI приложения.
    - Добавить ссылку на документацию OpenAPI (`/docs`).
