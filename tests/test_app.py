import pytest
import os
os.environ["DB_PATH"] = "/tmp/test_weatherops.db"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"

def test_get_cities():
    r = client.get("/api/cities/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_create_city():
    payload = {"name": "TestCity", "country": "TC", "lat": 10.0, "lon": 20.0}
    r = client.post("/api/cities/", json=payload)
    assert r.status_code == 201
    assert r.json()["name"] == "TestCity"

def test_get_city_not_found():
    r = client.get("/api/cities/99999")
    assert r.status_code == 404

def test_get_all_weather():
    r = client.get("/api/weather/all")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_get_stats():
    r = client.get("/api/weather/stats")
    assert r.status_code == 200
    assert "cities_monitored" in r.json()

def test_get_alerts():
    r = client.get("/api/alerts/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_create_alert_invalid_type():
    payload = {
        "city_id": 1,
        "city_name": "Tunis",
        "alert_type": "invalid",
        "threshold": 35.0,
        "condition": "gt"
    }
    r = client.post("/api/alerts/", json=payload)
    assert r.status_code == 400

def test_dashboard_page():
    r = client.get("/")
    assert r.status_code == 200

def test_alerts_page():
    r = client.get("/alerts")
    assert r.status_code == 200

def test_map_page():
    r = client.get("/map")
    assert r.status_code == 200