import httpx
from typing import List
from src.models.fuel_station import FuelStation, FuelType

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
