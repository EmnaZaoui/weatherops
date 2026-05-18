import os
os.environ["DB_PATH"] = "/tmp/test_weatherops.db"

import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

asyncio.run(init_db())

def test_health():
    with TestClient(app) as c:
        r = c.get("/health")
        assert r.status_code == 200

def test_get_cities():
    with TestClient(app) as c:
        r = c.get("/api/cities/")
        assert r.status_code == 200

def test_create_city():
    with TestClient(app) as c:
        r = c.post("/api/cities/", json={"name": "TestCity", "country": "TC", "lat": 10.0, "lon": 20.0})
        assert r.status_code in [201, 400]

def test_get_city_not_found():
    with TestClient(app) as c:
        r = c.get("/api/cities/99999")
        assert r.status_code == 404

def test_get_all_weather():
    with TestClient(app) as c:
        r = c.get("/api/weather/all")
        assert r.status_code == 200

def test_get_stats():
    with TestClient(app) as c:
        r = c.get("/api/weather/stats")
        assert r.status_code == 200

def test_get_alerts():
    with TestClient(app) as c:
        r = c.get("/api/alerts/")
        assert r.status_code == 200

def test_create_alert_invalid_type():
    with TestClient(app) as c:
        r = c.post("/api/alerts/", json={"city_id": 1, "city_name": "Tunis", "alert_type": "invalid", "threshold": 35.0, "condition": "gt"})
        assert r.status_code == 400

def test_dashboard_page():
    with TestClient(app) as c:
        r = c.get("/")
        assert r.status_code == 200

def test_alerts_page():
    with TestClient(app) as c:
        r = c.get("/alerts")
        assert r.status_code == 200

def test_map_page():
    with TestClient(app) as c:
        r = c.get("/map")
        assert r.status_code == 200