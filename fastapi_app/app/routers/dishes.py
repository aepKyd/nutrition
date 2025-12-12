from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import psycopg2
from app.database.session import get_db_connection
from app.schemas.schemas import CookedDish, CookedDishCreate, RemainingDish
from app.services import common as services

router = APIRouter()

@router.get("/remaining", response_model=List[RemainingDish])
def get_remaining_dishes(limit: int = 100, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        return services.get_remaining_dishes(conn, limit)
    except psycopg2.Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

@router.get("/", response_model=List[CookedDish])
def get_cooked_dishes(limit: int = 100, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        return services.get_cooked_dishes(conn, limit)
    except psycopg2.Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

@router.post("/", response_model=CookedDish, status_code=status.HTTP_201_CREATED)
def create_cooked_dish(dish: CookedDishCreate, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        new_dish = services.create_cooked_dish(conn, dish)
        conn.commit()
        return new_dish
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")

@router.get("/{dish_id}", response_model=CookedDish)
def get_cooked_dish(dish_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    dish = services.get_cooked_dish_by_id(conn, dish_id)
    if not dish:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cooked dish not found")
    return dish

@router.delete("/{dish_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cooked_dish(dish_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        services.delete_cooked_dish(conn, dish_id)
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return