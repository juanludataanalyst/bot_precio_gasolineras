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
