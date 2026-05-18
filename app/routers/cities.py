from fastapi import APIRouter, Depends, HTTPException
import aiosqlite

from app.database import get_db
from app.models.schemas import CityCreate, CityResponse

router = APIRouter()

@router.get("/")
async def get_all_cities(db: aiosqlite.Connection = Depends(get_db)):
    """Get all cities."""
    cursor = await db.execute("SELECT * FROM cities ORDER BY name")
    cities = await cursor.fetchall()
    return [dict(row) for row in cities]

@router.get("/{city_id}")
async def get_city(city_id: int, db: aiosqlite.Connection = Depends(get_db)):
    """Get a specific city."""
    cursor = await db.execute("SELECT * FROM cities WHERE id = ?", (city_id,))
    city = await cursor.fetchone()
    if not city:
        raise HTTPException(status_code=404, detail="Ville non trouvée")
    return dict(city)

@router.post("/", status_code=201)
async def create_city(city: CityCreate, db: aiosqlite.Connection = Depends(get_db)):
    """Create a new city."""
    cursor = await db.execute(
        "SELECT id FROM cities WHERE name = ? AND country = ?",
        (city.name, city.country)
    )
    if await cursor.fetchone():
        raise HTTPException(status_code=400, detail="Cette ville existe déjà")
    
    cursor = await db.execute(
        "INSERT INTO cities (name, country, lat, lon) VALUES (?, ?, ?, ?)",
        (city.name, city.country, city.lat, city.lon)
    )
    await db.commit()
    
    new_id = cursor.lastrowid
    cursor = await db.execute("SELECT * FROM cities WHERE id = ?", (new_id,))
    return dict(await cursor.fetchone())

@router.put("/{city_id}")
async def update_city(city_id: int, city: CityCreate, db: aiosqlite.Connection = Depends(get_db)):
    """Update a city."""
    cursor = await db.execute("SELECT id FROM cities WHERE id = ?", (city_id,))
    if not await cursor.fetchone():
        raise HTTPException(status_code=404, detail="Ville non trouvée")
    
    await db.execute(
        "UPDATE cities SET name = ?, country = ?, lat = ?, lon = ? WHERE id = ?",
        (city.name, city.country, city.lat, city.lon, city_id)
    )
    await db.commit()
    
    cursor = await db.execute("SELECT * FROM cities WHERE id = ?", (city_id,))
    return dict(await cursor.fetchone())

@router.delete("/{city_id}")
async def delete_city(city_id: int, db: aiosqlite.Connection = Depends(get_db)):
    """Delete a city and its related data."""
    cursor = await db.execute("SELECT id FROM cities WHERE id = ?", (city_id,))
    if not await cursor.fetchone():
        raise HTTPException(status_code=404, detail="Ville non trouvée")
    
    await db.execute("DELETE FROM weather_history WHERE city_id = ?", (city_id,))
    await db.execute("DELETE FROM alerts WHERE city_id = ?", (city_id,))
    await db.execute("DELETE FROM cities WHERE id = ?", (city_id,))
    await db.commit()
    
    return {"message": "Ville et données associées supprimées", "id": city_id}

@router.get("/search/{query}")
async def search_cities_geocoding(query: str):
    """Search cities via OpenWeatherMap Geocoding API."""
    import httpx
    import os
    
    api_key = os.getenv("OPENWEATHER_API_KEY", "demo")
    if api_key == "demo":
        # Return mock search results
        mock_results = [
            {"name": query, "country": "FR", "lat": 48.8566, "lon": 2.3522, "state": ""},
            {"name": query + " Centre", "country": "FR", "lat": 47.3900, "lon": 0.6893, "state": "Centre-Val de Loire"},
        ]
        return mock_results[:3]
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "http://api.openweathermap.org/geo/1.0/direct",
                params={"q": query, "limit": 5, "appid": api_key}
            )
            if response.status_code == 200:
                results = response.json()
                return [
                    {
                        "name": r.get("name"),
                        "country": r.get("country"),
                        "lat": r.get("lat"),
                        "lon": r.get("lon"),
                        "state": r.get("state", ""),
                    }
                    for r in results
                ]
    except Exception:
        pass
    return []

   
 
