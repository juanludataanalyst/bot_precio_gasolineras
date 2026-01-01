# Bot de Telegram - Precios de Gasolineras

Bot de Telegram que encuentra las 3 gasolineras más baratas cercanas a tu ubicación usando datos oficiales del Ministerio de Industria y Turismo de España.

## Características

- Ubicación GPS desde Telegram
- Todos los tipos de combustible
- Búsqueda por radio de distancia
- Datos en tiempo real del Ministerio
- Interfaz conversacional fácil de usar
- API REST para integración externa

## Instalación

### Requisitos Previos

- Python 3.12 o superior
- Token del bot de Telegram (obtenido desde [@BotFather](https://t.me/BotFather))

### Configuración Local

1. Clonar el repositorio:
```bash
git clone <repository-url>
cd bot_precio_gasolineras
```

2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
```

Editar el archivo `.env` y añadir tu token:
```
TELEGRAM_BOT_TOKEN=tu_token_aqui
PORT=8000
```

## Uso

### Ejecutar el Bot

```bash
python -m src.bot.main
```

### Comandos del Bot

- `/start` - Iniciar el bot y ver instrucciones
- `/cancel` - Cancelar la operación actual
- Compartir ubicación - Enviar tu ubicación GPS para buscar gasolineras cercanas

## API Endpoints

El bot también expone una API REST:

- `GET /health` - Health check
- `GET /api/fuel-stations?lat={lat}&lon={lon}&radio={radio}&fuel_type={type}` - Find cheapest stations
- `GET /docs` - API documentation (OpenAPI)

### Ejemplo de uso de la API

```bash
curl "http://localhost:8000/api/fuel-stations?lat=40.4168&lon=-3.7038&radio=5&fuel_type=Gasolina 95 E5"
```

## Despliegue

Para instrucciones detalladas de despliegue en diferentes plataformas, consulta [DEPLOYMENT.md](DEPLOYMENT.md).

### Opciones de Despliegue

- **Railway** - Despliegue continuo desde GitHub
- **Render** - Web service gratuito
- **Docker** - Contenedor para cualquier plataforma
- **Local** - Desarrollo y pruebas

## Tests

Ejecutar la suite de tests:

```bash
pytest -v
```

## Estructura del Proyecto

```
bot_precio_gasolineras/
├── src/
│   ├── api/           # API FastAPI
│   ├── bot/           # Bot de Telegram
│   ├── models/        # Modelos de datos
│   ├── services/      # Lógica de negocio
│   └── config.py      # Configuración
├── tests/             # Tests
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Licencia

MIT License
