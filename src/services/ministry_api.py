import urllib.request
import urllib.error
import json
import ssl
import logging
import time
import os
import asyncio
from typing import List
from src.models.fuel_station import FuelStation, FuelType

MINISTRY_API_URL = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/"
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1.0

logger = logging.getLogger(__name__)

class MinistryAPIClient:
    def __init__(self, http_client=None):
        self._http_client = http_client

    async def get_all_stations(self) -> List[FuelStation]:
        """Fetch all fuel stations from the Ministry API with automatic retries"""
        last_error = None

        print()
        print("=" * 60)
        print("🚀 MINISTRY API: Starting request")
        print(f"📍 URL: {MINISTRY_API_URL}")
        print(f"🔢 Max retries: {MAX_RETRIES}")
        print(f"🐳 Container ID: {os.environ.get('HOSTNAME', 'unknown')[:8]}")
        print("=" * 60)

        for attempt in range(MAX_RETRIES):
            start_time = time.time()

            try:
                print(f"📡 Attempt {attempt + 1}/{MAX_RETRIES}: Fetching with urllib")
                print(f"🔧 Using urllib with SSL context (no verification)")

                # Create SSL context that doesn't verify certificates
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

                # Make request using urllib
                req = urllib.request.Request(
                    MINISTRY_API_URL,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )

                with urllib.request.urlopen(req, timeout=60, context=ssl_context) as response:
                    elapsed = time.time() - start_time
                    print(f"✅ Response received in {elapsed:.2f}s")
                    print(f"📊 Status: {response.status}")

                    data = json.loads(response.read().decode('utf-8'))
                    print(f"✅ JSON parsed successfully")

                if attempt > 0:
                    print(f"🎉 Success on retry {attempt + 1}!")

                stations = self._parse_stations(data)
                print(f"✅ Parsed {len(stations)} fuel stations")

                return stations

            except (urllib.error.URLError, urllib.error.HTTPError, ssl.SSLError) as e:
                elapsed = time.time() - start_time
                last_error = e
                retry_delay = INITIAL_RETRY_DELAY * (2 ** attempt)

                print()
                print("❌" * 30)
                print(f"❌ NETWORK ERROR on attempt {attempt + 1}/{MAX_RETRIES}")
                print("❌" * 30)
                print(f"⏱️ Time to error: {elapsed:.2f}s")
                print(f"🔧 Error type: {type(e).__name__}")
                print(f"📝 Error message: {str(e)}")
                print(f"🌐 Target URL: {MINISTRY_API_URL}")
                print(f"🐳 Container: {os.environ.get('HOSTNAME', 'unknown')[:8]}")

                if hasattr(e, '__cause__') and e.__cause__:
                    print(f"🔍 Root cause: {type(e.__cause__).__name__}: {str(e.__cause__)}")

                if attempt < MAX_RETRIES - 1:
                    print(f"⏳ Waiting {retry_delay:.1f}s before retry...")
                    print()
                    await asyncio.sleep(retry_delay)
                else:
                    print()
                    print("💀" * 30)
                    print(f"💀 FAILED AFTER {MAX_RETRIES} ATTEMPTS")
                    print("💀" * 30)
                    print()

            except Exception as e:
                elapsed = time.time() - start_time
                print()
                print("❌" * 30)
                print(f"❌ UNEXPECTED ERROR (not retrying)")
                print("❌" * 30)
                print(f"⏱️ Time to error: {elapsed:.2f}s")
                print(f"🔧 Error type: {type(e).__name__}")
                print(f"📝 Error message: {str(e)}")
                print()
                raise

        print("💀 All retry attempts exhausted. Raising last error.")
        raise last_error if last_error else Exception("Unknown error occurred")

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
