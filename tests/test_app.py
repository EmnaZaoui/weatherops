import pytest
import asyncio
import os

os.environ["DB_PATH"] = "/tmp/test_weatherops.db"

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def client():
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

@pytest.mark.asyncio(loop_scope="session")
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"

@pytest.mark.asyncio(loop_scope="session")
async def test_get_cities(client):
    r = await client.get("/api/cities/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

@pytest.mark.asyncio(loop_scope="session")
async def test_create_city(client):
    payload = {"name": "TestCity", "country": "TC", "lat": 10.0, "lon": 20.0}
    r = await client.post("/api/cities/", json=payload)
    assert r.status_code == 201
    assert r.json()["name"] == "TestCity"

@pytest.mark.asyncio(loop_scope="session")
async def test_get_city_not_found(client):
    r = await client.get("/api/cities/99999")
    assert r.status_code == 404

@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_weather(client):
    r = await client.get("/api/weather/all")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

@pytest.mark.asyncio(loop_scope="session")
async def test_get_stats(client):
    r = await client.get("/api/weather/stats")
    assert r.status_code == 200
    assert "cities_monitored" in r.json()

@pytest.mark.asyncio(loop_scope="session")
async def test_get_alerts(client):
    r = await client.get("/api/alerts/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

@pytest.mark.asyncio(loop_scope="session")
async def test_create_alert_invalid_type(client):
    payload = {
        "city_id": 1,
        "city_name": "Tunis",
        "alert_type": "invalid",
        "threshold": 35.0,
        "condition": "gt"
    }
    r = await client.post("/api/alerts/", json=payload)
    assert r.status_code == 400

@pytest.mark.asyncio(loop_scope="session")
async def test_dashboard_page(client):
    r = await client.get("/")
    assert r.status_code == 200

@pytest.mark.asyncio(loop_scope="session")
async def test_alerts_page(client):
    r = await client.get("/alerts")
    assert r.status_code == 200

@pytest.mark.asyncio(loop_scope="session")
async def test_map_page(client):
    r = await client.get("/map")
    assert r.status_code == 200