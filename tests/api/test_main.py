import pytest
from httpx import AsyncClient, ASGITransport
from src.api.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_fuel_stations_endpoint_missing_params():
    """Test that endpoint returns 422 with missing parameters"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/fuel-stations")

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_fuel_stations_endpoint_invalid_radius():
    """Test that radius > 100 is rejected"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/fuel-stations?lat=40.4168&lon=-3.7038&radius=150&fuel_type=Gasolina+95+E5"
        )

    assert response.status_code == 422
