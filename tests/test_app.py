import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
import os

os.environ["DB_PATH"] = "/tmp/test_weatherops.db"

from app.main import app

@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

# ===== HEALTH =====
@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"

# ===== CITIES CRUD =====
@pytest.mark.asyncio
async def test_get_cities(client):
    r = await client.get("/api/cities/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

@pytest.mark.asyncio
async def test_create_city(client):
    payload = {"name": "TestCity", "country": "TC", "lat": 10.0, "lon": 20.0}
    r = await client.post("/api/cities/", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "TestCity"
    assert data["country"] == "TC"
    return data["id"]

@pytest.mark.asyncio
async def test_create_city_duplicate(client):
    payload = {"name": "TestCity", "country": "TC", "lat": 10.0, "lon": 20.0}
    r = await client.post("/api/cities/", json=payload)
    assert r.status_code == 400

@pytest.mark.asyncio
async def test_get_city_not_found(client):
    r = await client.get("/api/cities/99999")
    assert r.status_code == 404

# ===== WEATHER =====
@pytest.mark.asyncio
async def test_get_all_weather(client):
    r = await client.get("/api/weather/all")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "weather" in data[0]
        assert "temp" in data[0]["weather"]

@pytest.mark.asyncio
async def test_get_stats(client):
    r = await client.get("/api/weather/stats")
    assert r.status_code == 200
    data = r.json()
    assert "cities_monitored" in data
    assert "active_alerts" in data

# ===== ALERTS CRUD =====
@pytest.mark.asyncio
async def test_get_alerts_empty(client):
    r = await client.get("/api/alerts/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

@pytest.mark.asyncio
async def test_create_alert_invalid_type(client):
    r = await client.get("/api/cities/")
    cities = r.json()
    if not cities:
        return
    city_id = cities[0]["id"]
    payload = {
        "city_id": city_id,
        "city_name": cities[0]["name"],
        "alert_type": "invalid_type",
        "threshold": 35.0,
        "condition": "gt"
    }
    r = await client.post("/api/alerts/", json=payload)
    assert r.status_code == 400

@pytest.mark.asyncio
async def test_create_and_delete_alert(client):
    r = await client.get("/api/cities/")
    cities = r.json()
    if not cities:
        return
    city = cities[0]
    payload = {
        "city_id": city["id"],
        "city_name": city["name"],
        "alert_type": "temperature",
        "threshold": 40.0,
        "condition": "gt",
        "message": "Test alerte chaleur"
    }
    r = await client.post("/api/alerts/", json=payload)
    assert r.status_code == 201
    alert_id = r.json()["id"]

    # Toggle
    r = await client.patch(f"/api/alerts/{alert_id}/toggle")
    assert r.status_code == 200

    # Delete
    r = await client.delete(f"/api/alerts/{alert_id}")
    assert r.status_code == 200

# ===== PAGES HTML =====
@pytest.mark.asyncio
async def test_dashboard_page(client):
    r = await client.get("/")
    assert r.status_code == 200
    assert "WeatherOps" in r.text

@pytest.mark.asyncio
async def test_alerts_page(client):
    r = await client.get("/alerts")
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_map_page(client):
    r = await client.get("/map")
<<<<<<< HEAD
    assert r.status_code == 200
=======
    assert r.status_code == 200
>>>>>>> 04545d62421a0742ac53ed111b5072899c582a02
