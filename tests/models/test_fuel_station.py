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
