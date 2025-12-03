from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import date
import psycopg2
import json
from app.database.session import get_db_connection
from app.schemas.schemas import DailySummary

router = APIRouter()

@router.get("/daily_summary", response_model=DailySummary)
def get_daily_summary(
    summary_date: date, conn: psycopg2.extensions.connection = Depends(get_db_connection)
):
    """
    Get daily nutrition summary for a specific date.
    """
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT nutrition.get_daily_summary(%s);", (summary_date,))
        result = cursor.fetchone()
        
        if result and result[0] and result[0].get('meals'):
            # The get_daily_summary function returns JSONB, so we need to parse it
            daily_summary_data = result[0]
            # Validate and return using Pydantic model
            return DailySummary(**daily_summary_data)
        
        raise HTTPException(status_code=404, detail="No summary found for this date.")

    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        cursor.close()
        conn.close()
