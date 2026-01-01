import pytest
from unittest.mock import AsyncMock, Mock
from src.services.ministry_api import MinistryAPIClient
from src.models.fuel_station import FuelStation, FuelType

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
    mock_response_obj = Mock()
    mock_response_obj.json.return_value = mock_response
    mock_response_obj.raise_for_status = Mock()
    mock_http_client.get.return_value = mock_response_obj

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
    mock_response_obj = Mock()
    mock_response_obj.json.return_value = mock_response
    mock_response_obj.raise_for_status = Mock()
    mock_http_client.get.return_value = mock_response_obj

    client = MinistryAPIClient(http_client=mock_http_client)
    stations = await client.get_all_stations()

    assert stations[0].latitud == 40.4168
    assert stations[0].longitud == -3.7038
