# Bot de Telegram - Precios de Gasolineras Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Telegram bot that finds the 3 cheapest gas stations near a user's location using the Spanish Ministry of Industry's public API.

**Architecture:** Monolithic Python application combining a Telegram bot (python-telegram-bot) and REST API (FastAPI). Async HTTP client (httpx) queries the Ministry API, filters stations by distance and fuel type, returns top 3 cheapest options.

**Tech Stack:** Python 3.12+, FastAPI, python-telegram-bot 20+, httpx, Pydantic, pytest, uvicorn

---

## Task 1: Initialize Project Structure

**Files:**
- Create: `README.md`
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `pytest.ini`
- Create: `Procfile`
- Create: `src/__init__.py`
- Create: `src/bot/__init__.py`
- Create: `src/api/__init__.py`
- Create: `tests/__init__.py`

**Step 1: Create README.md**

```bash
cat > README.md << 'EOF'
# Bot de Telegram - Precios de Gasolineras

Bot de Telegram que encuentra las 3 gasolineras más baratas cercanas a tu ubicación usando datos oficiales del Ministerio de Industria y Turismo de España.

## Características

- Ubicación GPS desde Telegram
- Todos los tipos de combustible
- Búsqueda por radio de distancia
- Datos en tiempo real del Ministerio

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
python -m src.bot.main
```

## API Endpoints

- `GET /health` - Health check
- `GET /api/fuel-stations?lat={lat}&lon={lon}&radio={radio}&fuel_type={type}` - Find cheapest stations
- `GET /docs` - API documentation (OpenAPI)
EOF
```

**Step 2: Create requirements.txt**

```bash
cat > requirements.txt << 'EOF'
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-telegram-bot==20.7
httpx==0.26.0
pydantic==2.5.3
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-mock==3.12.0
EOF
```

**Step 3: Create .gitignore**

```bash
cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.env
.venv
env/
venv/
ENV/
.pytest_cache/
.coverage
htmlcov/
.DS_Store
*.log
EOF
```

**Step 4: Create pytest.ini**

```bash
cat > pytest.ini << 'EOF'
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
EOF
```

**Step 5: Create Procfile**

```bash
cat > Procfile << 'EOF'
web: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
worker: python -m src.bot.main
EOF
```

**Step 6: Create directory structure**

```bash
mkdir -p src/bot src/api tests
touch src/__init__.py src/bot/__init__.py src/api/__init__.py tests/__init__.py
```

**Step 7: Initialize git repository**

```bash
git init
git add .
git commit -m "chore: initialize project structure"
```

---

## Task 2: Define Data Models

**Files:**
- Create: `src/models/__init__.py`
- Create: `src/models/fuel_station.py`
- Create: `tests/models/test_fuel_station.py`

**Step 1: Write failing tests for FuelStation model**

Create `tests/models/test_fuel_station.py`:

```python
import pytest
from pydantic import ValidationError
from src.models.fuel_station import FuelStation, FuelType

def test_fuel_station_creation_with_valid_data():
    station = FuelStation(
        id="1234",
        rotulo="Repsol",
        direccion="Calle Falsa 123",
        municipio="Madrid",
        provincia="Madrid",
        latitud=40.4168,
        longitud=-3.7038,
        precios={
            FuelType.GASOLINA_95_E5: 1.459,
            FuelType.GASOLEO_A: 1.349
        }
    )

    assert station.id == "1234"
    assert station.rotulo == "Repsol"
    assert station.latitud == 40.4168
    assert station.longitud == -3.7038
    assert station.precios[FuelType.GASOLINA_95_E5] == 1.459

def test_fuel_station_validation_invalid_latitude():
    with pytest.raises(ValidationError):
        FuelStation(
            id="1234",
            rotulo="Repsol",
            direccion="Calle Falsa 123",
            municipio="Madrid",
            provincia="Madrid",
            latitud=100.0,  # Invalid: > 90
            longitud=-3.7038,
            precios={}
        )

def test_fuel_station_validation_invalid_longitude():
    with pytest.raises(ValidationError):
        FuelStation(
            id="1234",
            rotulo="Repsol",
            direccion="Calle Falsa 123",
            municipio="Madrid",
            provincia="Madrid",
            latitud=40.4168,
            longitud=200.0,  # Invalid: > 180
            precios={}
        )

def test_fuel_type_enum():
    assert FuelType.GASOLINA_95_E5.value == "Gasolina 95 E5"
    assert FuelType.GASOLEO_A.value == "Gasóleo A"
    assert len(FuelType) >= 2  # At least these two types
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/models/test_fuel_station.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'src.models'"

**Step 3: Create FuelStation model**

Create `src/models/__init__.py`:

```python
from .fuel_station import FuelStation, FuelType

__all__ = ["FuelStation", "FuelType"]
```

Create `src/models/fuel_station.py`:

```python
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Dict

class FuelType(str, Enum):
    GASOLINA_95_E5 = "Gasolina 95 E5"
    GASOLINA_98_E5 = "Gasolina 98 E5"
    GASOLEO_A = "Gasóleo A"
    GASOLEO_B = "Gasóleo B"
    GASOLEO_PREMIUM = "Gasóleo Premium"
    BIOETANOL = "Bioetanol"
    BIODIESEL = "Biodisel"
    GASES_LICUADOS = "Gases Licuados del Petróleo"
    GAS_NATURAL = "Gas Natural Comprimido"
    GAS_NATURAL Licuado = "Gas Natural Licuado"
    HIDROGENO = "Hidrógeno"

class FuelStation(BaseModel):
    id: str
    rotulo: str
    direccion: str
    municipio: str
    provincia: str
    latitud: float = Field(ge=-90, le=90)
    longitud: float = Field(ge=-180, le=180)
    precios: Dict[FuelType, float]

    @field_validator('latitud')
    @classmethod
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitud must be between -90 and 90')
        return v

    @field_validator('longitud')
    @classmethod
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitud must be between -180 and 180')
        return v
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/models/test_fuel_station.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/models tests/models
git commit -m "feat: add FuelStation and FuelType models with validation"
```

---

## Task 3: Implement Geographic Distance Calculation

**Files:**
- Create: `src/services/geo.py`
- Create: `tests/services/test_geo.py`

**Step 1: Write failing tests for Haversine formula**

Create `tests/services/test_geo.py`:

```python
import pytest
from src.services.geo import calculate_distance

def test_calculate_distance_same_point():
    """Distance from a point to itself should be 0"""
    lat, lon = 40.4168, -3.7038  # Madrid
    distance = calculate_distance(lat, lon, lat, lon)
    assert distance == 0.0

def test_calculate_distance_madrid_barcelona():
    """Distance between Madrid and Barcelona should be approximately 505 km"""
    madrid_lat, madrid_lon = 40.4168, -3.7038
    barcelona_lat, barcelona_lon = 41.3851, 2.1734

    distance = calculate_distance(madrid_lat, madrid_lon, barcelona_lat, barcelona_lon)

    # Should be approximately 505 km, allow 1% tolerance
    assert 500 <= distance <= 510

def test_calculate_distance_small_distance():
    """Small distance: approximately 1 km"""
    lat1, lon1 = 40.4168, -3.7038
    # ~1km north
    lat2, lon2 = 40.4258, -3.7038

    distance = calculate_distance(lat1, lon1, lat2, lon2)

    # Should be approximately 1 km, allow 10% tolerance
    assert 0.9 <= distance <= 1.1
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/services/test_geo.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'src.services'"

**Step 3: Implement Haversine formula**

Create `src/services/__init__.py`:

```python
from .geo import calculate_distance

__all__ = ["calculate_distance"]
```

Create `src/services/geo.py`:

```python
import math

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth
    using the Haversine formula.

    Returns distance in kilometers.
    """
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(dlon / 2) ** 2)

    c = 2 * math.asin(math.sqrt(a))

    # Radius of Earth in kilometers
    r = 6371

    return c * r
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/services/test_geo.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/services tests/services
git commit -m "feat: implement Haversine distance calculation"
```

---

## Task 4: Implement Ministry API Client

**Files:**
- Create: `src/services/ministry_api.py`
- Create: `tests/services/test_ministry_api.py`

**Step 1: Write failing tests for API client**

Create `tests/services/test_ministry_api.py`:

```python
import pytest
from unittest.mock import AsyncMock, patch
from src.services.ministry_api import MinistryAPIClient
from src.models import FuelStation, FuelType

@pytest.mark.asyncio
async def test_get_all_stations_success():
    """Test successful fetching of all stations"""
    mock_response = {
        "ListaEESSPrecio": [
            {
                "IDEESS": "1234",
                "Rótulo": "Repsol",
                "Dirección": "Calle Falsa 123",
                "Municipio": "Madrid",
                "Provincia": "Madrid",
                "Latitud": "40,4168",
                "Longitud (WGS84)": "-003,7038",
                "Precio Gasolina 95 E5": "1,459",
                "Precio Gasóleo A": "1,349"
            }
        ]
    }

    mock_http_client = AsyncMock()
    mock_http_client.get.return_value.json.return_value = mock_response
    mock_http_client.get.return_value.raise_for_status = AsyncMock()

    client = MinistryAPIClient(http_client=mock_http_client)
    stations = await client.get_all_stations()

    assert len(stations) == 1
    assert stations[0].id == "1234"
    assert stations[0].rotulo == "Repsol"
    assert stations[0].latitud == 40.4168
    assert stations[0].longitud == -3.7038

@pytest.mark.asyncio
async def test_get_all_stations_handles_decimal_separator():
    """Test that Spanish decimal comma is converted to point"""
    mock_response = {
        "ListaEESSPrecio": [
            {
                "IDEESS": "1234",
                "Rótulo": "Test",
                "Dirección": "Test",
                "Municipio": "Test",
                "Provincia": "Test",
                "Latitud": "40,4168",
                "Longitud (WGS84)": "-003,7038",
                "Precio Gasolina 95 E5": "1,459",
            }
        ]
    }

    mock_http_client = AsyncMock()
    mock_http_client.get.return_value.json.return_value = mock_response
    mock_http_client.get.return_value.raise_for_status = AsyncMock()

    client = MinistryAPIClient(http_client=mock_http_client)
    stations = await client.get_all_stations()

    assert stations[0].latitud == 40.4168
    assert stations[0].longitud == -3.7038
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/services/test_ministry_api.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'src.services.ministry_api'"

**Step 3: Implement Ministry API client**

Create `src/services/ministry_api.py`:

```python
import httpx
from typing import List
from src.models import FuelStation, FuelType

MINISTRY_API_URL = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/"

class MinistryAPIClient:
    def __init__(self, http_client: httpx.AsyncClient | None = None):
        self._http_client = http_client

    async def get_all_stations(self) -> List[FuelStation]:
        """Fetch all fuel stations from the Ministry API"""
        if self._http_client is None:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(MINISTRY_API_URL)
                response.raise_for_status()
                data = response.json()
        else:
            response = await self._http_client.get(MINISTRY_API_URL)
            response.raise_for_status()
            data = response.json()

        return self._parse_stations(data)

    def _parse_stations(self, data: dict) -> List[FuelStation]:
        """Parse Ministry API response into FuelStation objects"""
        stations = []

        for item in data.get("ListaEESSPrecio", []):
            # Parse coordinates (Spanish format uses comma as decimal separator)
            lat_str = item.get("Latitud", "0").replace(",", ".")
            lon_str = item.get("Longitud (WGS84)", "0").replace(",", ".")

            try:
                latitud = float(lat_str)
                longitud = float(lon_str)
            except (ValueError, TypeError):
                continue  # Skip stations with invalid coordinates

            # Extract prices for all fuel types
            precios = {}
            for fuel_type in FuelType:
                price_key = f"Precio {fuel_type.value}"
                price_str = item.get(price_key, "")

                if price_str:
                    try:
                        # Spanish format uses comma as decimal separator
                        price_float = float(price_str.replace(",", "."))
                        precios[fuel_type] = price_float
                    except (ValueError, TypeError):
                        pass

            station = FuelStation(
                id=item.get("IDEESS", ""),
                rotulo=item.get("Rótulo", "Desconocido"),
                direccion=item.get("Dirección", ""),
                municipio=item.get("Municipio", ""),
                provincia=item.get("Provincia", ""),
                latitud=latitud,
                longitud=longitud,
                precios=precios
            )

            stations.append(station)

        return stations
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/services/test_ministry_api.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/services/ministry_api.py tests/services/test_ministry_api.py
git commit -m "feat: implement Ministry API client with data parsing"
```

---

## Task 5: Implement Fuel Station Finder Service

**Files:**
- Create: `src/services/finder.py`
- Create: `tests/services/test_finder.py`

**Step 1: Write failing tests for finder service**

Create `tests/services/test_finder.py`:

```python
import pytest
from src.services.finder import FuelStationFinder
from src.models import FuelStation, FuelType

@pytest.mark.asyncio
async def test_find_cheapest_stations_filters_by_distance():
    """Test that only stations within radius are returned"""
    stations = [
        FuelStation(
            id="1",
            rotulo="Near Station",
            direccion="Near",
            municipio="Madrid",
            provincia="Madrid",
            latitud=40.4168,
            longitud=-3.7038,
            precios={FuelType.GASOLINA_95_E5: 1.500}
        ),
        FuelStation(
            id="2",
            rotulo="Far Station",
            direccion="Far",
            municipio="Barcelona",
            provincia="Barcelona",
            latitud=41.3851,
            longitud=2.1734,
            precios={FuelType.GASOLINA_95_E5: 1.300}
        )
    ]

    finder = FuelStationFinder()
    results = await finder.find_cheapest(
        stations=stations,
        user_lat=40.4168,
        user_lon=-3.7038,
        radius_km=10,
        fuel_type=FuelType.GASOLINA_95_E5
    )

    assert len(results) == 1
    assert results[0].id == "1"

@pytest.mark.asyncio
async def test_find_cheapest_stations_orders_by_price():
    """Test that stations are ordered by price (cheapest first)"""
    stations = [
        FuelStation(
            id="1",
            rotulo="Expensive",
            direccion="Test",
            municipio="Madrid",
            provincia="Madrid",
            latitud=40.4168,
            longitud=-3.7038,
            precios={FuelType.GASOLINA_95_E5: 1.500}
        ),
        FuelStation(
            id="2",
            rotulo="Cheap",
            direccion="Test",
            municipio="Madrid",
            provincia="Madrid",
            latitud=40.4170,
            longitud=-3.7040,
            precios={FuelType.GASOLINA_95_E5: 1.300}
        ),
        FuelStation(
            id="3",
            rotulo="Medium",
            direccion="Test",
            municipio="Madrid",
            provincia="Madrid",
            latitud=40.4172,
            longitud=-3.7042,
            precios={FuelType.GASOLINA_95_E5: 1.400}
        )
    ]

    finder = FuelStationFinder()
    results = await finder.find_cheapest(
        stations=stations,
        user_lat=40.4168,
        user_lon=-3.7038,
        radius_km=10,
        fuel_type=FuelType.GASOLINA_95_E5
    )

    assert len(results) == 3
    assert results[0].id == "2"  # Cheapest
    assert results[1].id == "3"  # Medium
    assert results[2].id == "1"  # Expensive

@pytest.mark.asyncio
async def test_find_cheapest_stations_limits_to_top_3():
    """Test that only top 3 cheapest stations are returned"""
    stations = []
    for i in range(10):
        stations.append(FuelStation(
            id=str(i),
            rotulo=f"Station {i}",
            direccion="Test",
            municipio="Madrid",
            provincia="Madrid",
            latitud=40.4168 + (i * 0.0001),
            longitud=-3.7038,
            precios={FuelType.GASOLINA_95_E5: 1.300 + (i * 0.01)}
        ))

    finder = FuelStationFinder()
    results = await finder.find_cheapest(
        stations=stations,
        user_lat=40.4168,
        user_lon=-3.7038,
        radius_km=10,
        fuel_type=FuelType.GASOLINA_95_E5
    )

    assert len(results) == 3

@pytest.mark.asyncio
async def test_find_cheapest_stations_filters_by_fuel_type():
    """Test that stations without the requested fuel type are excluded"""
    stations = [
        FuelStation(
            id="1",
            rotulo="With Gasolina",
            direccion="Test",
            municipio="Madrid",
            provincia="Madrid",
            latitud=40.4168,
            longitud=-3.7038,
            precios={FuelType.GASOLINA_95_E5: 1.500}
        ),
        FuelStation(
            id="2",
            rotulo="Without Gasolina",
            direccion="Test",
            municipio="Madrid",
            provincia="Madrid",
            latitud=40.4170,
            longitud=-3.7040,
            precios={FuelType.GASOLEO_A: 1.400}
        )
    ]

    finder = FuelStationFinder()
    results = await finder.find_cheapest(
        stations=stations,
        user_lat=40.4168,
        user_lon=-3.7038,
        radius_km=10,
        fuel_type=FuelType.GASOLINA_95_E5
    )

    assert len(results) == 1
    assert results[0].id == "1"
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/services/test_finder.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'src.services.finder'"

**Step 3: Implement finder service**

Create `src/services/finder.py`:

```python
from typing import List
from src.models import FuelStation, FuelType
from src.services.geo import calculate_distance

class FuelStationFinder:
    async def find_cheapest(
        self,
        stations: List[FuelStation],
        user_lat: float,
        user_lon: float,
        radius_km: float,
        fuel_type: FuelType
    ) -> List[FuelStation]:
        """
        Find the cheapest fuel stations within a given radius.

        Args:
            stations: List of all fuel stations
            user_lat: User's latitude
            user_lon: User's longitude
            radius_km: Search radius in kilometers
            fuel_type: Type of fuel to search for

        Returns:
            List of up to 3 cheapest stations, ordered by price
        """
        # Filter stations that have the requested fuel type
        valid_stations = [
            station for station in stations
            if fuel_type in station.precios
        ]

        # Filter by distance
        stations_in_radius = []
        for station in valid_stations:
            distance = calculate_distance(
                user_lat, user_lon,
                station.latitud, station.longitud
            )

            if distance <= radius_km:
                # Store distance for later use
                station._distance = distance  # type: ignore
                stations_in_radius.append(station)

        # Sort by price (cheapest first)
        stations_in_radius.sort(
            key=lambda s: s.precios[fuel_type]
        )

        # Return top 3
        return stations_in_radius[:3]
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/services/test_finder.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/services/finder.py tests/services/test_finder.py
git commit -m "feat: implement fuel station finder service"
```

---

## Task 6: Implement FastAPI Application

**Files:**
- Create: `src/api/main.py`
- Create: `tests/api/test_main.py`

**Step 1: Write failing tests for API endpoints**

Create `tests/api/test_main.py`:

```python
import pytest
from httpx import AsyncClient
from src.api.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_fuel_stations_endpoint_missing_params():
    """Test that endpoint returns 422 with missing parameters"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/fuel-stations")

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_fuel_stations_endpoint_invalid_radius():
    """Test that radius > 100 is rejected"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/fuel-stations?lat=40.4168&lon=-3.7038&radius=150&fuel_type=Gasolina+95+E5"
        )

    assert response.status_code == 422
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/api/test_main.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'src.api.main'"

**Step 3: Implement FastAPI application**

Create `src/api/main.py`:

```python
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field, validator
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

    @validator('fuel_type')
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
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/api/test_main.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/api tests/api
git commit -m "feat: implement FastAPI application with endpoints"
```

---

## Task 7: Implement Telegram Bot - Conversation Handlers

**Files:**
- Create: `src/bot/handlers.py`
- Create: `tests/bot/test_handlers.py`

**Step 1: Write failing tests for bot handlers**

Create `tests/bot/test_handlers.py`:

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch
from telegram import Update, User, Chat, Location
from telegram.ext import ContextTypes
from src.bot.handlers import start_command, help_command, cancel_command

@pytest.mark.asyncio
async def test_start_command():
    """Test /start command sends welcome message"""
    update = Mock(spec=Update)
    update.effective_message = AsyncMock()
    update.effective_message.reply_text = AsyncMock()

    context = Mock(spec=ContextTypes.DEFAULT_TYPE)

    await start_command(update, context)

    update.effective_message.reply_text.assert_called_once()
    args = update.effective_message.reply_text.call_args[0]
    assert "ubicación" in args[0].lower()

@pytest.mark.asyncio
async def test_cancel_command():
    """Test /cancel command cancels conversation"""
    update = Mock(spec=Update)
    update.effective_message = AsyncMock()
    update.effective_message.reply_text = AsyncMock()

    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}

    await cancel_command(update, context)

    update.effective_message.reply_text.assert_called_once()
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/bot/test_handlers.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'src.bot.handlers'"

**Step 3: Implement bot handlers**

Create `src/bot/handlers.py`:

```python
from telegram import Update
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask for location"""
    await update.message.reply_text(
        "👋 ¡Hola! Soy el bot de precios de gasolineras.\n\n"
        "Para encontrar las gasolineras más baratas cerca de ti, "
        "necesito que me compartas tu ubicación.\n\n"
        "📍 Pulsa el clip 📎 y selecciona 'Ubicación' o usa el botón de ubicación.",
        reply_markup=get_location_keyboard()
    )
    return 1

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message"""
    help_text = (
        "🤖 *Ayuda del Bot*\n\n"
        "Para encontrar las gasolineras más baratas:\n"
        "1. Pulsa /start para comenzar\n"
        "2. Comparte tu ubicación GPS\n"
        "3. Selecciona el tipo de combustible\n"
        "4. Indica el radio de búsqueda en km\n\n"
        "Comandos disponibles:\n"
        "/start - Iniciar búsqueda\n"
        "/help - Mostrar esta ayuda\n"
        "/cancel - Cancelar búsqueda",
        parse_mode='Markdown'
    )
    await update.message.reply_text(help_text)

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation"""
    await update.message.reply_text(
        "❌ Búsqueda cancelada. Pulsa /start para comenzar de nuevo."
    )
    context.user_data.clear()
    return -1

def get_location_keyboard():
    """Create keyboard with location button"""
    from telegram import ReplyKeyboardMarkup, KeyboardButton

    keyboard = [
        [KeyboardButton("📍 Compartir mi ubicación", request_location=True)]
    ]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/bot/test_handlers.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/bot/handlers.py tests/bot/test_handlers.py
git commit -m "feat: implement basic bot command handlers"
```

---

## Task 8: Implement Telegram Bot - Conversation Flow

**Files:**
- Create: `src/bot/conversation.py`
- Create: `tests/bot/test_conversation.py`

**Step 1: Write failing tests for conversation flow**

Create `tests/bot/test_conversation.py`:

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch
from telegram import Update, User, Chat, Location
from telegram.ext import ContextTypes
from src.bot.conversation import (
    location_handler,
    fuel_type_callback,
    radius_handler
)

@pytest.mark.asyncio
async def test_location_handler_saves_location():
    """Test that location is saved in user_data"""
    update = Mock(spec=Update)
    update.message = AsyncMock()
    update.message.location = Mock(latitude=40.4168, longitude=-3.7038)
    update.message.reply_text = AsyncMock()

    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}

    await location_handler(update, context)

    assert context.user_data['latitude'] == 40.4168
    assert context.user_data['longitude'] == -3.7038

@pytest.mark.asyncio
async def test_radius_handler_validates_positive_number():
    """Test that radius must be a positive number"""
    update = Mock(spec=Update)
    update.message = AsyncMock()
    update.message.text = "5"
    update.message.reply_text = AsyncMock()

    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {'latitude': 40.4168, 'longitude': -3.7038, 'fuel_type': 'Gasolina 95 E5'}

    result = await radius_handler(update, context)

    # Should proceed to next step (return ConversationHandler.END)
    assert result is not None
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/bot/test_conversation.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'src.bot.conversation'"

**Step 3: Implement conversation flow**

Create `src/bot/conversation.py`:

```python
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.models import FuelType
from src.services.ministry_api import MinistryAPIClient
from src.services.finder import FuelStationFinder

# Conversation states
LOCATION, FUEL_TYPE, RADIUS = range(3)

async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user's location and ask for fuel type"""
    user_location = update.message.location

    # Save location
    context.user_data['latitude'] = user_location.latitude
    context.user_data['longitude'] = user_location.longitude

    # Show fuel type options
    keyboard = []
    for fuel_type in FuelType:
        keyboard.append([InlineKeyboardButton(
            fuel_type.value,
            callback_data=f"fuel_{fuel_type.value}"
        )])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "⛽ ¿Qué tipo de combustible buscas?",
        reply_markup=reply_markup
    )

    return FUEL_TYPE

async def fuel_type_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle fuel type selection and ask for radius"""
    query = update.callback_query
    await query.answer()

    # Extract fuel type from callback data
    fuel_type = query.data.replace("fuel_", "")
    context.user_data['fuel_type'] = fuel_type

    await query.edit_message_text(
        f"✅ Combustible seleccionado: *{fuel_type}*\n\n"
        "📏 Ahora indica el radio de búsqueda en kilómetros.\n\n"
        "Ejemplos: 5, 10, 20",
        parse_mode='Markdown'
    )

    return RADIUS

async def radius_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle radius input and find cheapest stations"""
    radius_text = update.message.text.strip()

    try:
        radius = float(radius_text)
        if radius <= 0 or radius > 100:
            await update.message.reply_text(
                "❌ El radio debe estar entre 1 y 100 km. Intenta de nuevo."
            )
            return RADIUS
    except ValueError:
        await update.message.reply_text(
            "❌ Por favor, ingresa un número válido. Ejemplo: 5, 10, 20"
        )
        return RADIUS

    # Get user data
    lat = context.user_data.get('latitude')
    lon = context.user_data.get('longitude')
    fuel_type_str = context.user_data.get('fuel_type')

    if not all([lat, lon, fuel_type_str]):
        await update.message.reply_text(
            "❌ Error en los datos. Por favor, empieza de nuevo con /start"
        )
        return ConversationHandler.END

    try:
        fuel_type = FuelType(fuel_type_str)
    except ValueError:
        await update.message.reply_text(
            "❌ Tipo de combustible inválido. Empieza de nuevo con /start"
        )
        return ConversationHandler.END

    # Send "searching" message
    status_message = await update.message.reply_text(
        "🔍 Buscando las gasolineras más baratas...\n\n"
        "Esto puede tardar unos segundos."
    )

    try:
        # Fetch stations and find cheapest
        api_client = MinistryAPIClient()
        all_stations = await api_client.get_all_stations()

        finder = FuelStationFinder()
        stations = await finder.find_cheapest(
            stations=all_stations,
            user_lat=lat,
            user_lon=lon,
            radius_km=radius,
            fuel_type=fuel_type
        )

        # Delete status message
        await status_message.delete()

        if not stations:
            await update.message.reply_text(
                f"❌ No encontré gasolineras con {fuel_type_str} "
                f"en un radio de {radius} km.\n\n"
                "💡 Intenta con un radio mayor.",
                reply_markup=get_restart_keyboard()
            )
        else:
            # Send results
            await send_results(update, stations, fuel_type)

    except Exception as e:
        await status_message.delete()
        await update.message.reply_text(
            f"❌ Error al buscar gasolineras: {str(e)}\n\n"
            "Por favor, intenta más tarde o usa /start para empezar de nuevo."
        )

    # Clear user data
    context.user_data.clear()

    return ConversationHandler.END

async def send_results(update: Update, stations, fuel_type: FuelType) -> None:
    """Send search results to user"""
    message = f"⛽ *Las {len(stations)} gasolineras más baratas*\n\n"

    for i, station in enumerate(stations, 1):
        distance = getattr(station, '_distance', 0.0)
        price = station.precios[fuel_type]

        message += (
            f"*{i}. {station.rotulo}*\n"
            f"💰 Precio: *{price:.3f} €/l*\n"
            f"📍 {station.direccion}\n"
            f"🏘️ {station.municipio}, {station.provincia}\n"
            f"📏 Distancia: {distance:.2f} km\n\n"
        )

    message += "✅ Datos oficiales del Ministerio de Industria y Turismo"

    await update.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=get_restart_keyboard()
    )

def get_restart_keyboard():
    """Create keyboard with restart button"""
    from telegram import ReplyKeyboardMarkup, KeyboardButton

    keyboard = [[KeyboardButton("/start")]]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/bot/test_conversation.py -v
```

Expected: PASS (some tests may need mocking adjustment)

**Step 5: Commit**

```bash
git add src/bot/conversation.py tests/bot/test_conversation.py
git commit -m "feat: implement conversation flow for bot"
```

---

## Task 9: Implement Telegram Bot - Main Application

**Files:**
- Create: `src/bot/main.py`

**Step 1: Create main bot application**

Create `src/bot/main.py`:

```python
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from src.bot import handlers, conversation

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get token from environment variable or use placeholder
import os
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

def main() -> None:
    """Start the bot"""
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", handlers.start_command))
    application.add_handler(CommandHandler("help", handlers.help_command))
    application.add_handler(CommandHandler("cancel", handlers.cancel_command))

    # Add conversation handler
    conv_handler = conversation.ConversationHandler(
        entry_points=[CommandHandler("start", handlers.start_command)],
        states={
            conversation.LOCATION: [
                MessageHandler(filters.LOCATION, conversation.location_handler)
            ],
            conversation.FUEL_TYPE: [
                CallbackQueryHandler(conversation.fuel_type_callback)
            ],
            conversation.RADIUS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, conversation.radius_handler)
            ],
        },
        fallbacks=[CommandHandler("cancel", handlers.cancel_command)],
    )

    application.add_handler(conv_handler)

    # Start the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
```

**Step 2: Run bot (for testing, will fail without token)**

```bash
python -m src.bot.main
```

Expected: ERROR if no token set, but code should run

**Step 3: Commit**

```bash
git add src/bot/main.py
git commit -m "feat: implement main bot application"
```

---

## Task 10: Add Environment Configuration

**Files:**
- Create: `.env.example`
- Create: `src/config.py`

**Step 1: Create environment example**

```bash
cat > .env.example << 'EOF'
# Telegram Bot Token (obtain from @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Port for web server (for cloud deployment)
PORT=8000
EOF
```

**Step 2: Create configuration module**

Create `src/config.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    PORT = int(os.getenv("PORT", "8000"))

    @classmethod
    def validate(cls):
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

config = Config()
```

**Step 3: Update requirements.txt to include python-dotenv**

```bash
echo "python-dotenv==1.0.0" >> requirements.txt
```

**Step 4: Commit**

```bash
git add .env.example src/config.py requirements.txt
git commit -m "feat: add environment configuration"
```

---

## Task 11: Create Docker Configuration (Optional)

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`

**Step 1: Create Dockerfile**

```bash
cat > Dockerfile << 'EOF'
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run the application
CMD ["python", "-m", "src.bot.main"]
EOF
```

**Step 2: Create docker-compose.yml**

```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  bot:
    build: .
    env_file:
      - .env
    restart: unless-stopped
EOF
```

**Step 3: Commit**

```bash
git add Dockerfile docker-compose.yml
git commit -m "feat: add Docker configuration"
```

---

## Task 12: Create Deployment Guide

**Files:**
- Create: `DEPLOYMENT.md`

**Step 1: Create deployment guide**

```bash
cat > DEPLOYMENT.md << 'EOF'
# Deployment Guide

## Local Development

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment:
```bash
cp .env.example .env
# Edit .env and add your TELEGRAM_BOT_TOKEN
```

4. Run the bot:
```bash
python -m src.bot.main
```

## Railway Deployment

1. Create a new project on Railway
2. Connect this repository
3. Add environment variable: `TELEGRAM_BOT_TOKEN`
4. Deploy

## Render Deployment

1. Create a new Web Service on Render
2. Connect this repository
3. Add environment variable: `TELEGRAM_BOT_TOKEN`
4. Set start command: `python -m src.bot.main`
5. Deploy

## Docker Deployment

1. Build image:
```bash
docker build -t bot-precio-gasolineras .
```

2. Run container:
```bash
docker run -d --name gasolineras-bot --env-file .env bot-precio-gasolineras
```

Or use docker-compose:
```bash
docker-compose up -d
```
EOF
```

**Step 2: Commit**

```bash
git add DEPLOYMENT.md
git commit -m "docs: add deployment guide"
```

---

## Task 13: Final Testing and Documentation

**Step 1: Run all tests**

```bash
pytest -v
```

Expected: All tests pass

**Step 2: Test bot manually**

1. Set up bot token with @BotFather
2. Run bot locally
3. Test complete flow in Telegram

**Step 3: Update README with full instructions**

Update `README.md` with:
- Full setup instructions
- Link to deployment guide
- Example usage screenshots (optional)

**Step 4: Final commit**

```bash
git add README.md
git commit -m "docs: update README with complete instructions"
```

**Step 5: Create tag**

```bash
git tag -a v1.0.0 -m "Release v1.0.0 - Initial release"
git push origin main --tags
```

---

## Summary

This implementation plan follows TDD, with each feature built test-first. The plan is organized into 13 tasks, each with small, verifiable steps.

**Total estimated implementation time:** 4-6 hours

**Key files created:**
- 15+ source files
- 10+ test files
- Configuration files for deployment
- Complete documentation

**Testing coverage:**
- Unit tests for all services
- Integration tests for bot and API
- Manual testing checklist
EOF
