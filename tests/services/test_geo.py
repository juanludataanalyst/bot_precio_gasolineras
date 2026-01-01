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
