from fastapi import APIRouter, Depends, HTTPException, status
from datetime import date
import psycopg2
from app.database.session import get_db_connection
from app.schemas.schemas import DailySummary
from app.services import stats as stats_service

router = APIRouter()

@router.get("/daily_summary", response_model=DailySummary)
def get_daily_summary(summary_date: date, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Get daily nutrition summary for a specific date.
    """
    try:
        daily_summary_data = stats_service.get_daily_summary(conn, summary_date)
        if daily_summary_data and daily_summary_data.get('meals'):
            return DailySummary(**daily_summary_data)
        
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No summary found for this date.")
    except psycopg2.Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")