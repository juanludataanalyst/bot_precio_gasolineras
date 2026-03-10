import aiohttp
import asyncio
import logging
import time
import socket
import os
from typing import List
from src.models.fuel_station import FuelStation, FuelType

MINISTRY_API_URL = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/"
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1.0  # seconds

logger = logging.getLogger(__name__)

class MinistryAPIClient:
    def __init__(self, http_client: aiohttp.ClientSession | None = None):
        self._http_client = http_client

    async def get_all_stations(self) -> List[FuelStation]:
        """Fetch all fuel stations from the Ministry API with automatic retries"""
        last_error = None

        # Use print for critical logs that must always be visible
        print()
        print("=" * 60)
        print("🚀 MINISTRY API: Starting request")
        print(f"📍 URL: {MINISTRY_API_URL}")
        print(f"🔢 Max retries: {MAX_RETRIES}")
        print(f"⏱️ Timeout: 60.0s")
        print(f"🐳 Container ID: {os.environ.get('HOSTNAME', 'unknown')[:8]}")
        print("=" * 60)

        for attempt in range(MAX_RETRIES):
            start_time = time.time()

            try:
                if self._http_client is None:
                    print(f"📡 Attempt {attempt + 1}/{MAX_RETRIES}: Creating HTTP client (aiohttp)")
                    print(f"🔧 Using aiohttp with SSL disabled and timeout=60s")

                    timeout = aiohttp.ClientTimeout(total=60)
                    connector = aiohttp.TCPConnector(ssl=False)

                    async with aiohttp.ClientSession(
                        timeout=timeout,
                        connector=connector
                    ) as session:
                        print(f"🔗 Session created successfully")
                        print(f"📨 Sending GET request...")

                        async with session.get(MINISTRY_API_URL) as response:
                            elapsed = time.time() - start_time
                            print(f"✅ Response received in {elapsed:.2f}s")
                            print(f"📊 Status: {response.status}")
                            print(f"📏 Size: {len(response.content)} bytes")

                            response.raise_for_status()

                            print(f"📦 Parsing JSON response...")
                            data = await response.json()
                            print(f"✅ JSON parsed successfully")
                else:
                    print(f"📡 Attempt {attempt + 1}/{MAX_RETRIES}: Using provided HTTP client")
                    response = await self._http_client.get(MINISTRY_API_URL)

                    elapsed = time.time() - start_time
                    print(f"✅ Response received in {elapsed:.2f}s")
                    print(f"📊 Status: {response.status_code}")

                    response.raise_for_status()
                    data = response.json()
                    print(f"✅ JSON parsed successfully")

                if attempt > 0:
                    print(f"🎉 Success on retry {attempt + 1}!")

                stations = self._parse_stations(data)
                print(f"✅ Parsed {len(stations)} fuel stations")

                return stations

            except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as e:
                elapsed = time.time() - start_time
                last_error = e
                retry_delay = INITIAL_RETRY_DELAY * (2 ** attempt)  # Exponential backoff: 1s, 2s, 4s

                print()
                print("❌" * 30)
                print(f"❌ NETWORK ERROR on attempt {attempt + 1}/{MAX_RETRIES}")
                print("❌" * 30)
                print(f"⏱️ Time to error: {elapsed:.2f}s")
                print(f"🔧 Error type: {type(e).__name__}")
                print(f"📝 Error message: {str(e)}")

                # Log additional context
                print(f"🌐 Target URL: {MINISTRY_API_URL}")
                print(f"🐳 Container: {os.environ.get('HOSTNAME', 'unknown')[:8]}")
                print(f"🔢 Attempt: {attempt + 1}/{MAX_RETRIES}")

                # Try to get more details about the error
                if hasattr(e, '__cause__') and e.__cause__:
                    print(f"🔍 Root cause: {type(e.__cause__).__name__}: {str(e.__cause__)}")

                # Network diagnostics
                print()
                print("🔬 Running network diagnostics...")
                try:
                    # Extract hostname from URL
                    from urllib.parse import urlparse
                    parsed_url = urlparse(MINISTRY_API_URL)
                    hostname = parsed_url.hostname

                    # Test DNS resolution
                    loop = asyncio.get_event_loop()
                    try:
                        result = await loop.getaddrinfo(hostname, 443, proto=socket.IPPROTO_TCP)
                        ips = [addr[4][0] for addr in result]
                        print(f"✅ DNS resolution works: {hostname} → {set(ips)}")
                    except Exception as dns_error:
                        print(f"❌ DNS resolution failed: {dns_error}")

                    # Test TCP connection
                    try:
                        reader, writer = await asyncio.wait_for(
                            asyncio.open_connection(hostname, 443),
                            timeout=5.0
                        )
                        print(f"✅ TCP connection to {hostname}:443 successful")
                        writer.close()
                        await writer.wait_closed()
                    except Exception as tcp_error:
                        print(f"❌ TCP connection failed: {type(tcp_error).__name__}: {tcp_error}")

                except Exception as diag_error:
                    print(f"⚠️ Diagnostics failed: {diag_error}")

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

            except httpx.HTTPStatusError as e:
                elapsed = time.time() - start_time
                print()
                print("❌" * 30)
                print(f"❌ HTTP STATUS ERROR (not retrying)")
                print("❌" * 30)
                print(f"⏱️ Time to error: {elapsed:.2f}s")
                print(f"📊 Status code: {e.response.status_code}")
                print(f"📝 Response: {e.response.text[:500]}")
                print()
                raise

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

        # If we exhausted all retries, raise the last error
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
