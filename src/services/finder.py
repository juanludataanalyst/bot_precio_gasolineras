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
