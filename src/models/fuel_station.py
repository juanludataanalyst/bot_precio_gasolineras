from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Dict

class FuelType(str, Enum):
    GASOLINA_95_E5 = "Gasolina 95 E5"
    GASOLINA_98_E5 = "Gasolina 98 E5"
    GASOLEO_A = "Gasoleo A"
    GASOLEO_B = "Gasoleo B"
    GASOLEO_PREMIUM = "Gasoleo Premium"
    BIOETANOL = "Bioetanol"
    BIODIESEL = "Biodiesel"
    GASES_LICUADOS = "Gases licuados del petróleo"
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

    @field_validator('precios')
    @classmethod
    def validate_prices_non_negative(cls, v):
        for fuel_type, price in v.items():
            if price < 0:
                raise ValueError(f'Price for {fuel_type} cannot be negative: {price}')
        return v
