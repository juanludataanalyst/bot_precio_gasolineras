# Bot de Telegram - Precios de Gasolineras en España

## Fecha
2026-01-01

## Descripción del Proyecto
Bot de Telegram que permite a los usuarios encontrar las 3 gasolineras más baratas cercanas a su ubicación, utilizando los datos oficiales del Ministerio de Industria y Turismo de España.

## Arquitectura

### Arquitectura General
Sistema monolítico en Python que combina un bot de Telegram y una API REST.

**Capa de Bot de Telegram**:
- Utilizando `python-telegram-bot` (versión 20+)
- Maneja interacción directa con usuarios mediante comandos y handlers
- ConversationHandler para flujo de 3 pasos: ubicación → tipo combustible → radio

**Capa de API FastAPI**:
- Framework web asíncrono
- Endpoints internos para consultas del bot
- Endpoints públicos opcionales para terceros
- Documentación OpenAPI automática

**Integración con API del Ministerio**:
- API pública del Ministerio de Industria y Turismo: `https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/`
- Cliente HTTP asíncrono con `httpx`

**Despliegue**:
- Cloud-ready para Railway/Render
- Servidor ASGI: `uvicorn`

## Stack Tecnológico
- **Python 3.12+**
- **FastAPI** - Framework web
- **python-telegram-bot 20+** - Bot de Telegram
- **httpx** - Cliente HTTP asíncrono
- **Pydantic** - Validación de datos
- **pytest** - Testing

## Componentes del Sistema

### 1. Bot de Telegram
**ConversationHandler** - Gestiona flujo de 3 pasos:
- Paso 1: Recibir ubicación (GPS del mensaje de Telegram)
- Paso 2: Seleccionar tipo de combustible (inline keyboard)
- Paso 3: Ingresar radio de búsqueda en km (validación numérica)

**Message Handlers**:
- `/start` - Inicia el flujo
- `/help` - Muestra instrucciones
- `/buscar` - Inicia nueva búsqueda
- `/cancel` - Cancela flujo actual

**Callback Handlers**:
- Maneja respuestas de inline keyboards

### 2. Cliente de la API del Ministerio
**HTTP Client (httpx)**:
- Petición asíncrona a la API pública del Ministerio
- Endpoint: `https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/`
- Parsea respuesta JSON/XML
- Timeout: 10 segundos

**Filtro Geográfico**:
- Calcula distancia usando fórmula Haversine
- Filtra estaciones dentro del radio
- Ordena por precio (ascendente)
- Devuelve top 3

### 3. API FastAPI
**Endpoints**:
- `GET /` - Health check
- `GET /health` - Health check para cloud providers
- `GET /api/fuel-stations` - Consulta pública opcional
  - Query params: `lat`, `lon`, `radio`, `fuel_type`
  - Devuelve top 3 gasolineras más baratas en JSON
- `GET /docs` - Documentación OpenAPI automática

### 4. Modelos de Datos
**FuelStation (Pydantic)**:
- `id`: str - ID único de la estación
- `rotulo`: str - Nombre/marca de la gasolinera
- `direccion`: str - Dirección postal
- `municipio`: str - Municipio
- `provincia`: str - Provincia
- `latitud`: float - Latitud
- `longitud`: float - Longitud
- `precios`: dict - Precios por tipo de combustible

**FuelType (Enum)**:
Todos los tipos de combustible disponibles en la API:
- Gasolina 95 E5
- Gasolina 98 E5
- Gasóleo A
- Y todos los tipos disponibles en la API

## Flujo de Datos

1. **Usuario inicia** → Envía `/start` al bot
2. **Bot solicita ubicación** → Usuario comparte GPS
3. **Bot presenta combustibles** → Inline keyboard con todos los tipos
4. **Usuario selecciona** → Callback con tipo seleccionado
5. **Bot solicita radio** → Usuario ingresa número (ej: "5")
6. **Bot consulta API** → Petición GET asíncrona a Ministerio
7. **Procesamiento**:
   - Parsear JSON/XML (~11,000 estaciones)
   - Filtrar por tipo de combustible
   - Calcular distancias (Haversine)
   - Filtrar por radio
   - Ordenar por precio
   - Seleccionar top 3
8. **Formatear respuesta** → Crear mensaje con resultados
9. **Enviar a usuario** → Bot responde

**Optimizaciones**:
- Petición HTTP asíncrona (no bloquea bot)
- Early filtering (filtra por combustible primero)
- Timeouts configurados
- Error handling con sugerencias

## Manejo de Errores

### Errores de la API del Ministerio
- **Timeout** (>10s): "El servicio está saturado, intenta más tarde"
- **Error 500/503**: Reintentar hasta 2 veces con backoff exponencial (1s, 2s)
- **Respuesta vacía**: "No hay datos disponibles, intenta más tarde"
- **Formato inesperado**: Loggear error, mensaje genérico al usuario

### Errores de entrada del usuario
- **Sin ubicación**: MVP solo acepta GPS de Telegram
- **Radio inválido**: Validar número positivo entre 1-100 km
- **Combustible sin precio**: Informar y sugerir otro tipo

### Casos sin resultados
- **Sin estaciones en radio**: "No encontré gasolineras en X km. ¿Quieres radio mayor?" + botones (×2, ×3)
- **Menos de 3 estaciones**: Devolver las que haya

### Errores del bot
- **Usuario cancela**: Comando `/cancel` en cualquier punto
- **Conversación abandonada**: Timeout 5 minutos, limpiar estado
- **Mensaje inesperado**: Recordar qué se necesita

### Validaciones
- Coordenadas: latitud -90 a 90, longitud -180 a 180
- Precio missing: Ignorar estación

## Testing

### Pruebas unitarias (pytest)
**Cliente API Ministerio**:
- Mock de respuesta con datos de prueba
- Test parsing JSON/XML a modelos Pydantic
- Test cálculo distancia Haversine (casos conocidos)
- Test filtrado por combustible
- Test ordenamiento por precio
- Test selección top 3

**Cálculos geográficos**:
- Test distancia coordenadas conocidas
- Test filtro por radio
- Test edge cases (radio=0, límites coordenadas)

### Pruebas de integración
**Bot handlers**:
- Test ConversationHandler con mock de Update
- Test flujo completo
- Test comando `/cancel`
- Test timeout conversación

### Pruebas manuales (Telegram)
**Casos de prueba**:
- Madrid centro, 5km, Gasolina 95 E5
- Zona rural, 20km, Gasóleo A
- Radio muy pequeño (0.5km) - sin resultados
- Radio muy grande (100km) - verificar performance
- Frontera (Málaga/Gibraltar)
- Cancelación a mitad de flujo

### Performance testing
- **Tiempo de respuesta**: <10 segundos total
  - Descarga: ~2-5s
  - Filtrado + cálculos: <1s
- **Memory usage**: Verificar parsing de 11k estaciones

### Mock data
- Subset de 50-100 estaciones reales para tests
- No llamar API real en tests automatizados

## API del Ministerio - Referencia

**Endpoint Principal**:
```
https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/
```

**Características**:
- Pública, sin autenticación
- Devuelve todas las estaciones de España
- Actualización diaria
- Formato JSON/XML
- ~11,000 estaciones

**Fuentes oficiales**:
- [Sede Electrónica - Precios de Carburantes](https://sede.serviciosmin.gob.es/es-es/datosabiertos/catalogo/precios-carburantes)
- [Datos.gob.es - Catálogo](https://datos.gob.es/es/catalogo/e05068001-precio-de-carburantes-en-las-gasolineras-espanolas)
- [Manual RISP API](https://www.miteco.gob.es/content/dam/miteco/es/energia/files-1/risp/EnvioInformacion/Documents/Manual_Integrador_RispAPI.pdf)

## Estrategia de Datos
- **Sin caché**: Consulta API en vivo cada petición
- Ventaja: Datos siempre actualizados
- Desventaja: Más lento, pero aceptable para MVP

## Despliegue
- **Plataforma**: Railway/Render
- **Configuración**:
  - `Procfile` para comandos de inicio
  - `requirements.txt` para dependencias
  - Variables de entorno mínimas (TOKEN_BOT_TELEGRAM)
- **Servidor**: uvicorn con workers configurables

## Próximos Pasos
1. Crear estructura del proyecto
2. Implementar modelos de datos
3. Implementar cliente API Ministerio
4. Implementar bot de Telegram
5. Implementar API FastAPI (opcional)
6. Testing unitario e integración
7. Despliegue en cloud
