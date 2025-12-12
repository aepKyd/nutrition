import psycopg2
from typing import Dict, Any
from datetime import date

def get_daily_summary(conn: psycopg2.extensions.connection, summary_date: date) -> Dict[str, Any]:
    with conn.cursor() as cursor:
        cursor.execute("SELECT nutrition.get_daily_summary(%s);", (summary_date,))
        result = cursor.fetchone()
        if result and result[0]:
            return result[0]
        return None
