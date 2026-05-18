from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
import aiosqlite
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.services.weather_service import fetch_weather_by_coords, fetch_forecast, fetch_air_quality
from app.services.alert_service import check_alerts

router = APIRouter()

@router.get("/current/{city_id}")
async def get_current_weather(city_id: int, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM cities WHERE id = ?", (city_id,))
    city = await cursor.fetchone()
    if not city:
        raise HTTPException(status_code=404, detail="Ville non trouvée")
    
    weather = await fetch_weather_by_coords(city["lat"], city["lon"], city["name"])
    if not weather:
        raise HTTPException(status_code=503, detail="Service météo indisponible")
    
    await db.execute("""
        INSERT INTO weather_history 
        (city_id, city_name, temperature, feels_like, humidity, pressure, wind_speed, wind_direction, description, icon, visibility, uv_index)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        city_id, city["name"], weather["temp"], weather["feels_like"],
        weather["humidity"], weather["pressure"], weather["wind_speed"],
        weather["wind_deg"], weather["description"], weather["icon"],
        weather.get("visibility"), weather.get("uv")
    ))
    await db.commit()
    
    triggered_alerts = await check_alerts(city_id, weather)
    
    return {
        "city_id": city_id,
        "city_name": city["name"],
        "country": city["country"],
        "lat": city["lat"],
        "lon": city["lon"],
        "weather": weather,
        "triggered_alerts": triggered_alerts,
        "recorded_at": datetime.now().isoformat()
    }

@router.get("/all")
async def get_all_weather(db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM cities")
    cities = await cursor.fetchall()
    
    import asyncio
    
    async def fetch_city_weather(city):
        weather = await fetch_weather_by_coords(city["lat"], city["lon"], city["name"])
        if weather:
            triggered = await check_alerts(city["id"], weather)
            return {
                "city_id": city["id"],
                "city_name": city["name"],
                "country": city["country"],
                "lat": city["lat"],
                "lon": city["lon"],
                "weather": weather,
                "triggered_alerts": triggered,
            }
        return None
    
    tasks = [fetch_city_weather(city) for city in cities]
    all_results = await asyncio.gather(*tasks)
    return [r for r in all_results if r is not None]

@router.get("/forecast/{city_id}")
async def get_forecast(city_id: int, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM cities WHERE id = ?", (city_id,))
    city = await cursor.fetchone()
    if not city:
        raise HTTPException(status_code=404, detail="Ville non trouvée")
    
    forecast = await fetch_forecast(city["lat"], city["lon"], city["name"])
    return {"city_id": city_id, "city_name": city["name"], "forecast": forecast}

@router.get("/history/{city_id}")
async def get_weather_history(city_id: int, limit: int = 24, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute(
        "SELECT * FROM weather_history WHERE city_id = ? ORDER BY recorded_at DESC LIMIT ?",
        (city_id, limit)
    )
    history = await cursor.fetchall()
    return [dict(row) for row in history]

@router.get("/air-quality/{city_id}")
async def get_air_quality(city_id: int, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM cities WHERE id = ?", (city_id,))
    city = await cursor.fetchone()
    if not city:
        raise HTTPException(status_code=404, detail="Ville non trouvée")
    
    air_quality = await fetch_air_quality(city["lat"], city["lon"])
    return {"city_name": city["name"], "air_quality": air_quality}

@router.get("/stats")
async def get_global_stats(db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT COUNT(*) as total FROM cities")
    city_count = (await cursor.fetchone())["total"]
    
    cursor = await db.execute("SELECT COUNT(*) as total FROM weather_history")
    history_count = (await cursor.fetchone())["total"]
    
    cursor = await db.execute("SELECT COUNT(*) as total FROM alerts WHERE active = 1")
    alert_count = (await cursor.fetchone())["total"]
    
    cursor = await db.execute("SELECT COUNT(*) as total FROM alerts WHERE triggered = 1")
    triggered_count = (await cursor.fetchone())["total"]
    
    return {
        "cities_monitored": city_count,
        "data_points": history_count,
        "active_alerts": alert_count,
        "triggered_alerts": triggered_count,
    }