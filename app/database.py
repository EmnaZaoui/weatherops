import aiosqlite
import os

DB_PATH = os.getenv("DB_PATH", "/app/data/weatherops.db")

async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()

async def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                country TEXT NOT NULL,
                lat REAL NOT NULL,
                lon REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city_id INTEGER NOT NULL,
                city_name TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                threshold REAL NOT NULL,
                condition TEXT NOT NULL,
                message TEXT,
                active INTEGER DEFAULT 1,
                triggered INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (city_id) REFERENCES cities(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS weather_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city_id INTEGER NOT NULL,
                city_name TEXT NOT NULL,
                temperature REAL,
                feels_like REAL,
                humidity INTEGER,
                pressure REAL,
                wind_speed REAL,
                wind_direction INTEGER,
                description TEXT,
                icon TEXT,
                visibility REAL,
                uv_index REAL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (city_id) REFERENCES cities(id)
            )
        """)
        # Insert default cities if empty
        cursor = await db.execute("SELECT COUNT(*) FROM cities")
        count = await cursor.fetchone()
        if count[0] == 0:
            default_cities = [
                ("Tunis", "TN", 36.8189, 10.1658),
                ("Paris", "FR", 48.8566, 2.3522),
                ("London", "GB", 51.5074, -0.1278),
                ("New York", "US", 40.7128, -74.0060),
                ("Tokyo", "JP", 35.6762, 139.6503),
            ]
            await db.executemany(
                "INSERT INTO cities (name, country, lat, lon) VALUES (?, ?, ?, ?)",
                default_cities
            )

        await db.commit()

