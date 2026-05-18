from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
import os

from app.routers import weather, alerts, cities, dashboard
from app.database import init_db

app = FastAPI(
    title="WeatherOps API",
    description="Dashboard Météo avec Alertes & Déploiement Automatisé",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "WeatherOps"}

app.include_router(weather.router, prefix="/api/weather", tags=["weather"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(cities.router, prefix="/api/cities", tags=["cities"])
app.include_router(dashboard.router, tags=["dashboard"])

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)