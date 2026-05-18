import httpx
import os
from typing import Optional, Dict, Any
import asyncio

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "demo")
BASE_URL = "https://api.openweathermap.org/data/2.5"
ONECALL_URL = "https://api.openweathermap.org/data/3.0/onecall"

# Demo/mock data when no API key
MOCK_WEATHER = {
    "Tunis": {"temp": 28.5, "feels_like": 30.1, "humidity": 65, "pressure": 1013, "wind_speed": 4.2, "wind_deg": 180, "description": "Ciel dégagé", "icon": "01d", "visibility": 10000, "uv": 6.5},
    "Paris": {"temp": 18.2, "feels_like": 17.5, "humidity": 72, "pressure": 1008, "wind_speed": 6.1, "wind_deg": 270, "description": "Nuageux", "icon": "04d", "visibility": 8000, "uv": 3.2},
    "London": {"temp": 15.0, "feels_like": 14.1, "humidity": 80, "pressure": 1005, "wind_speed": 7.8, "wind_deg": 220, "description": "Pluie légère", "icon": "10d", "visibility": 6000, "uv": 2.1},
    "New York": {"temp": 22.3, "feels_like": 23.5, "humidity": 60, "pressure": 1015, "wind_speed": 5.5, "wind_deg": 90, "description": "Partiellement nuageux", "icon": "02d", "visibility": 10000, "uv": 5.8},
    "Tokyo": {"temp": 24.8, "feels_like": 26.2, "humidity": 70, "pressure": 1012, "wind_speed": 3.9, "wind_deg": 135, "description": "Brume", "icon": "50d", "visibility": 5000, "uv": 4.3},
}

async def fetch_weather_by_coords(lat: float, lon: float, city_name: str) -> Optional[Dict[str, Any]]:
    """Fetch weather from OpenWeatherMap API or return mock data."""
    if OPENWEATHER_API_KEY == "demo" or OPENWEATHER_API_KEY == "":
        return _get_mock_weather(city_name)
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/weather",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": OPENWEATHER_API_KEY,
                    "units": "metric",
                    "lang": "fr"
                }
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "temp": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"],
                    "wind_speed": data["wind"]["speed"],
                    "wind_deg": data["wind"].get("deg", 0),
                    "description": data["weather"][0]["description"].capitalize(),
                    "icon": data["weather"][0]["icon"],
                    "visibility": data.get("visibility", 10000),
                    "uv": 0,
                    "sunrise": data["sys"].get("sunrise"),
                    "sunset": data["sys"].get("sunset"),
                }
            else:
                return _get_mock_weather(city_name)
    except Exception:
        return _get_mock_weather(city_name)

async def fetch_forecast(lat: float, lon: float, city_name: str) -> list:
    """Fetch 5-day forecast."""
    if OPENWEATHER_API_KEY == "demo" or OPENWEATHER_API_KEY == "":
        return _get_mock_forecast(city_name)
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/forecast",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": OPENWEATHER_API_KEY,
                    "units": "metric",
                    "lang": "fr",
                    "cnt": 40
                }
            )
            if response.status_code == 200:
                data = response.json()
                forecasts = []
                seen_dates = set()
                for item in data["list"]:
                    date = item["dt_txt"].split(" ")[0]
                    if date not in seen_dates and len(forecasts) < 7:
                        seen_dates.add(date)
                        forecasts.append({
                            "date": date,
                            "temp_max": item["main"]["temp_max"],
                            "temp_min": item["main"]["temp_min"],
                            "description": item["weather"][0]["description"].capitalize(),
                            "icon": item["weather"][0]["icon"],
                            "humidity": item["main"]["humidity"],
                            "wind_speed": item["wind"]["speed"],
                        })
                return forecasts
            else:
                return _get_mock_forecast(city_name)
    except Exception:
        return _get_mock_forecast(city_name)

def _get_mock_weather(city_name: str) -> Dict[str, Any]:
    """Return mock weather data."""
    import random, math
    base = MOCK_WEATHER.get(city_name, MOCK_WEATHER["Tunis"])
    variation = random.uniform(-2, 2)
    return {
        "temp": round(base["temp"] + variation, 1),
        "feels_like": round(base["feels_like"] + variation, 1),
        "humidity": base["humidity"] + random.randint(-5, 5),
        "pressure": base["pressure"] + random.randint(-3, 3),
        "wind_speed": round(base["wind_speed"] + random.uniform(-1, 1), 1),
        "wind_deg": base["wind_deg"],
        "description": base["description"],
        "icon": base["icon"],
        "visibility": base["visibility"],
        "uv": base["uv"],
    }

def _get_mock_forecast(city_name: str) -> list:
    """Return mock 7-day forecast."""
    import random
    from datetime import datetime, timedelta
    
    base = MOCK_WEATHER.get(city_name, MOCK_WEATHER["Tunis"])
    forecasts = []
    icons = ["01d", "02d", "03d", "04d", "10d", "01d", "02d"]
    descs = ["Ensoleillé", "Partiellement nuageux", "Nuageux", "Couvert", "Pluie légère", "Ensoleillé", "Partiellement nuageux"]
    
    for i in range(7):
        date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        temp_base = base["temp"] + random.uniform(-4, 4)
        forecasts.append({
            "date": date,
            "temp_max": round(temp_base + random.uniform(2, 5), 1),
            "temp_min": round(temp_base - random.uniform(2, 5), 1),
            "description": descs[i],
            "icon": icons[i],
            "humidity": base["humidity"] + random.randint(-10, 10),
            "wind_speed": round(base["wind_speed"] + random.uniform(-2, 2), 1),
        })
    return forecasts

async def fetch_air_quality(lat: float, lon: float) -> Optional[Dict]:
    """Fetch air quality data."""
    if OPENWEATHER_API_KEY == "demo":
        import random
        aqi_labels = ["Bon", "Acceptable", "Modéré", "Mauvais", "Très mauvais"]
        aqi = random.randint(1, 4)
        return {
            "aqi": aqi,
            "label": aqi_labels[aqi - 1],
            "pm2_5": round(random.uniform(5, 50), 1),
            "pm10": round(random.uniform(10, 80), 1),
            "no2": round(random.uniform(10, 100), 1),
            "o3": round(random.uniform(20, 180), 1),
        }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/air_pollution",
                params={"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY}
            )
            if response.status_code == 200:
                data = response.json()
                aqi_labels = ["Bon", "Acceptable", "Modéré", "Mauvais", "Très mauvais"]
                aqi = data["list"][0]["main"]["aqi"]
                components = data["list"][0]["components"]
                return {
                    "aqi": aqi,
                    "label": aqi_labels[aqi - 1],
                    "pm2_5": components.get("pm2_5", 0),
                    "pm10": components.get("pm10", 0),
                    "no2": components.get("no2", 0),
                    "o3": components.get("o3", 0),
                }
    except Exception:
        pass
    return None
