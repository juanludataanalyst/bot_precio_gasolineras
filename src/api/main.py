from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import List
from src.models import FuelStation, FuelType
from src.services.ministry_api import MinistryAPIClient
from src.services.finder import FuelStationFinder

app = FastAPI(
    title="Bot Precios Gasolineras API",
    description="API para encontrar las gasolineras más baratas de España",
    version="1.0.0"
)

class FuelStationResponse(BaseModel):
    id: str
    rotulo: str
    direccion: str
    municipio: str
    provincia: str
    latitud: float
    longitud: float
    precio: float
    distancia_km: float

class FuelStationsRequest(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    radius: float = Field(gt=0, le=100)
    fuel_type: str

    @field_validator('fuel_type')
    def validate_fuel_type(cls, v):
        try:
            FuelType(v)
        except ValueError:
            raise ValueError(f"Invalid fuel type: {v}")
        return v

@app.get("/")
async def root():
    return {"message": "Bot de Telegram - Precios de Gasolineras API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/fuel-stations", response_model=List[FuelStationResponse])
async def find_fuel_stations(
    lat: float = Query(ge=-90, le=90, description="Latitud del usuario"),
    lon: float = Query(ge=-180, le=180, description="Longitud del usuario"),
    radius: float = Query(gt=0, le=100, description="Radio de búsqueda en km"),
    fuel_type: str = Query(description="Tipo de combustible")
):
    """Find the cheapest fuel stations within a given radius"""
    try:
        fuel_enum = FuelType(fuel_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid fuel type: {fuel_type}")

    # Fetch all stations from Ministry API
    api_client = MinistryAPIClient()
    all_stations = await api_client.get_all_stations()

    # Find cheapest stations
    finder = FuelStationFinder()
    stations = await finder.find_cheapest(
        stations=all_stations,
        user_lat=lat,
        user_lon=lon,
        radius_km=radius,
        fuel_type=fuel_enum
    )

    # Convert to response format
    response = []
    for station in stations:
        distance = getattr(station, '_distance', 0.0)
        response.append(FuelStationResponse(
            id=station.id,
            rotulo=station.rotulo,
            direccion=station.direccion,
            municipio=station.municipio,
            provincia=station.provincia,
            latitud=station.latitud,
            longitud=station.longitud,
            precio=station.precios[fuel_enum],
            distancia_km=round(distance, 2)
        ))

    return response
