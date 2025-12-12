from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import date
import psycopg2
from app.database.session import get_db_connection
from app.schemas.schemas import Consumed, ConsumedCreate, ConsumedUpdate
from app.services import common as services

router = APIRouter()

@router.get("/", response_model=List[Consumed])
def get_consumed_items(consumed_date: Optional[date] = None, limit: int = 100, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        return services.get_consumed_items(conn, consumed_date, limit)
    except psycopg2.Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

@router.post("/", response_model=Consumed, status_code=status.HTTP_201_CREATED)
def create_consumed_item(consumed_item: ConsumedCreate, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        new_consumed_item = services.create_consumed_item(conn, consumed_item)
        conn.commit()
        return new_consumed_item
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")

@router.get("/{consumed_id}", response_model=Consumed)
def get_consumed_item(consumed_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    item = services.get_consumed_item_by_id(conn, consumed_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consumed item not found")
    return item

@router.put("/{consumed_id}", response_model=Consumed)
def update_consumed_item(consumed_id: int, item: ConsumedUpdate, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        updated_item = services.update_consumed_item(conn, consumed_id, item)
        if not updated_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consumed item not found")
        conn.commit()
        return updated_item
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")

@router.delete("/{consumed_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_consumed_item(consumed_id: int, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        deleted_count = services.delete_consumed_item(conn, consumed_id)
        if deleted_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consumed item not found")
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {e}")
    return