import aiosqlite
import os
from typing import List, Dict

DB_PATH = os.getenv("DB_PATH", "/app/data/weatherops.db")

async def check_alerts(city_id: int, weather_data: dict) -> List[Dict]:
    """Check if any alerts are triggered for a city based on current weather."""
    triggered = []
    
    metric_map = {
        "temperature": weather_data.get("temp", 0),
        "humidity": weather_data.get("humidity", 0),
        "wind_speed": weather_data.get("wind_speed", 0),
        "pressure": weather_data.get("pressure", 0),
    }
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM alerts WHERE city_id = ? AND active = 1",
            (city_id,)
        )
        alerts = await cursor.fetchall()
        
        for alert in alerts:
            current_value = metric_map.get(alert["alert_type"], 0)
            is_triggered = False
            
            if alert["condition"] == "gt" and current_value > alert["threshold"]:
                is_triggered = True
            elif alert["condition"] == "lt" and current_value < alert["threshold"]:
                is_triggered = True
            
            if is_triggered:
                triggered.append({
                    "id": alert["id"],
                    "city_name": alert["city_name"],
                    "alert_type": alert["alert_type"],
                    "threshold": alert["threshold"],
                    "condition": alert["condition"],
                    "current_value": current_value,
                    "message": alert["message"],
                })
                # Update triggered status
                await db.execute(
                    "UPDATE alerts SET triggered = 1 WHERE id = ?",
                    (alert["id"],)
                )
        
        await db.commit()
    
    return triggered

async def reset_alert_triggers(city_id: int):
    """Reset triggered status for alerts (called after weather update)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE alerts SET triggered = 0 WHERE city_id = ?",
            (city_id,)
        )
        await db.commit()
