from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# City Models
class CityCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    country: str = Field(..., min_length=2, max_length=10)
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)

class CityResponse(BaseModel):
    id: int
    name: str
    country: str
    lat: float
    lon: float
    created_at: Optional[str] = None

# Alert Models
class AlertCreate(BaseModel):
    city_id: int
    city_name: str
    alert_type: str = Field(..., description="temperature, humidity, wind_speed, pressure")
    threshold: float
    condition: str = Field(..., description="gt (greater than) or lt (less than)")
    message: Optional[str] = None

class AlertUpdate(BaseModel):
    alert_type: Optional[str] = None
    threshold: Optional[float] = None
    condition: Optional[str] = None
    message: Optional[str] = None
    active: Optional[int] = None

class AlertResponse(BaseModel):
    id: int
    city_id: int
    city_name: str
    alert_type: str
    threshold: float
    condition: str
    message: Optional[str]
    active: int
    triggered: int
    created_at: Optional[str] = None

# Weather Models
class WeatherData(BaseModel):
    city_id: int
    city_name: str
    temperature: float
    feels_like: float
    humidity: int
    pressure: float
    wind_speed: float
    wind_direction: int
    description: str
    icon: str
    visibility: Optional[float] = None
    uv_index: Optional[float] = None

class WeatherHistoryResponse(BaseModel):
    id: int
    city_id: int
    city_name: str
    temperature: float
    feels_like: float
    humidity: int
    pressure: float
    wind_speed: float
    wind_direction: int
    description: str
    icon: str
    visibility: Optional[float]
    uv_index: Optional[float]
<<<<<<< HEAD
    recorded_at: str
=======
    recorded_at: str
>>>>>>> 04545d62421a0742ac53ed111b5072899c582a02
