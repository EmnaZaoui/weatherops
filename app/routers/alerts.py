from fastapi import APIRouter, Depends, HTTPException
import aiosqlite
from typing import List

from app.database import get_db
from app.models.schemas import AlertCreate, AlertUpdate, AlertResponse

router = APIRouter()

@router.get("/")
async def get_all_alerts(db: aiosqlite.Connection = Depends(get_db)):
    """Get all alerts."""
    cursor = await db.execute("SELECT * FROM alerts ORDER BY created_at DESC")
    alerts = await cursor.fetchall()
    return [dict(row) for row in alerts]

@router.get("/{alert_id}")
async def get_alert(alert_id: int, db: aiosqlite.Connection = Depends(get_db)):
    """Get a specific alert."""
    cursor = await db.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,))
    alert = await cursor.fetchone()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    return dict(alert)

@router.post("/", status_code=201)
async def create_alert(alert: AlertCreate, db: aiosqlite.Connection = Depends(get_db)):
    """Create a new alert."""
    # Verify city exists
    cursor = await db.execute("SELECT id FROM cities WHERE id = ?", (alert.city_id,))
    city = await cursor.fetchone()
    if not city:
        raise HTTPException(status_code=404, detail="Ville non trouvée")
    
    valid_types = ["temperature", "humidity", "wind_speed", "pressure"]
    if alert.alert_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Type invalide. Valeurs acceptées: {valid_types}")
    
    if alert.condition not in ["gt", "lt"]:
        raise HTTPException(status_code=400, detail="Condition doit être 'gt' ou 'lt'")
    
    cursor = await db.execute("""
        INSERT INTO alerts (city_id, city_name, alert_type, threshold, condition, message)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (alert.city_id, alert.city_name, alert.alert_type, alert.threshold, alert.condition, alert.message))
    await db.commit()
    
    new_id = cursor.lastrowid
    cursor = await db.execute("SELECT * FROM alerts WHERE id = ?", (new_id,))
    return dict(await cursor.fetchone())

@router.put("/{alert_id}")
async def update_alert(alert_id: int, alert: AlertUpdate, db: aiosqlite.Connection = Depends(get_db)):
    """Update an alert."""
    cursor = await db.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,))
    existing = await cursor.fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    
    updates = {k: v for k, v in alert.dict().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="Aucune mise à jour fournie")
    
    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [alert_id]
    
    await db.execute(f"UPDATE alerts SET {set_clause} WHERE id = ?", values)
    await db.commit()
    
    cursor = await db.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,))
    return dict(await cursor.fetchone())

@router.delete("/{alert_id}")
async def delete_alert(alert_id: int, db: aiosqlite.Connection = Depends(get_db)):
    """Delete an alert."""
    cursor = await db.execute("SELECT id FROM alerts WHERE id = ?", (alert_id,))
    if not await cursor.fetchone():
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    
    await db.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
    await db.commit()
    return {"message": "Alerte supprimée avec succès", "id": alert_id}

@router.patch("/{alert_id}/toggle")
async def toggle_alert(alert_id: int, db: aiosqlite.Connection = Depends(get_db)):
    """Toggle alert active status."""
    cursor = await db.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,))
    alert = await cursor.fetchone()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    
    new_status = 0 if alert["active"] == 1 else 1
    await db.execute("UPDATE alerts SET active = ? WHERE id = ?", (new_status, alert_id))
    await db.commit()
    
    return {"id": alert_id, "active": new_status, "message": "Statut mis à jour"}

    return {"id": alert_id, "active": new_status, "message": "Statut mis à jour"}

