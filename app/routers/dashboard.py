from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import aiosqlite

from app.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: aiosqlite.Connection = Depends(get_db)):
    """Main dashboard page."""
    cursor = await db.execute("SELECT * FROM cities ORDER BY name")
    cities = await cursor.fetchall()
    
    cursor = await db.execute("SELECT COUNT(*) as total FROM alerts WHERE active = 1")
    alert_count = (await cursor.fetchone())["total"]
    
    cursor = await db.execute("SELECT COUNT(*) as total FROM alerts WHERE triggered = 1")
    triggered_count = (await cursor.fetchone())["total"]
    
    cursor = await db.execute("SELECT COUNT(*) as total FROM weather_history")
    history_count = (await cursor.fetchone())["total"]
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "cities": [dict(c) for c in cities],
        "alert_count": alert_count,
        "triggered_count": triggered_count,
        "history_count": history_count,
    })

@router.get("/city/{city_id}", response_class=HTMLResponse)
async def city_detail(request: Request, city_id: int, db: aiosqlite.Connection = Depends(get_db)):
    """City detail page."""
    cursor = await db.execute("SELECT * FROM cities WHERE id = ?", (city_id,))
    city = await cursor.fetchone()
    if not city:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    
    cursor = await db.execute(
        "SELECT * FROM alerts WHERE city_id = ? ORDER BY created_at DESC",
        (city_id,)
    )
    alerts = await cursor.fetchall()
    
    cursor = await db.execute(
        "SELECT * FROM weather_history WHERE city_id = ? ORDER BY recorded_at DESC LIMIT 24",
        (city_id,)
    )
    history = await cursor.fetchall()
    
    return templates.TemplateResponse("city_detail.html", {
        "request": request,
        "city": dict(city),
        "alerts": [dict(a) for a in alerts],
        "history": [dict(h) for h in history],
    })

@router.get("/alerts", response_class=HTMLResponse)
async def alerts_page(request: Request, db: aiosqlite.Connection = Depends(get_db)):
    """Alerts management page."""
    cursor = await db.execute("""
        SELECT a.*, c.name as city_name 
        FROM alerts a 
        JOIN cities c ON a.city_id = c.id 
        ORDER BY a.created_at DESC
    """)
    alerts = await cursor.fetchall()
    
    cursor = await db.execute("SELECT * FROM cities ORDER BY name")
    cities = await cursor.fetchall()
    
    return templates.TemplateResponse("alerts.html", {
        "request": request,
        "alerts": [dict(a) for a in alerts],
        "cities": [dict(c) for c in cities],
    })

@router.get("/map", response_class=HTMLResponse)
async def map_page(request: Request, db: aiosqlite.Connection = Depends(get_db)):
    """World map page."""
    cursor = await db.execute("SELECT * FROM cities ORDER BY name")
    cities = await cursor.fetchall()
    
    return templates.TemplateResponse("map.html", {
        "request": request,
        "cities": [dict(c) for c in cities],

    })
