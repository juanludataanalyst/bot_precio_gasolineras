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
