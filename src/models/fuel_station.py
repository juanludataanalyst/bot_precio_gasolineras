from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Dict

class FuelType(str, Enum):
    GASOLINA_95_E5 = "Gasolina 95 E5"
    GASOLINA_98_E5 = "Gasolina 98 E5"
    GASOLEO_A = "Gasóleo A"
    GASOLEO_B = "Gasóleo B"
    GASOLEO_PREMIUM = "Gasóleo Premium"
    BIOETANOL = "Bioetanol"
    BIODIESEL = "Biodisel"
    GASES_LICUADOS = "Gases Licuados del Petróleo"
    GAS_NATURAL = "Gas Natural Comprimido"
    GAS_NATURAL_LICUADO = "Gas Natural Licuado"
    HIDROGENO = "Hidrógeno"

class FuelStation(BaseModel):
    id: str
    rotulo: str
    direccion: str
    municipio: str
    provincia: str
    latitud: float = Field(ge=-90, le=90)
    longitud: float = Field(ge=-180, le=180)
    precios: Dict[FuelType, float]

    @field_validator('latitud')
    @classmethod
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitud must be between -90 and 90')
        return v

    @field_validator('longitud')
    @classmethod
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitud must be between -180 and 180')
        return v
