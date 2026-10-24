from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IngresoCreate(BaseModel):
    idVehiculo: int
    idOperario: int
    idCelda: int | None = None


class RegistroOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idRegistro: int
    fechaIngreso: datetime
    fechaSalida: datetime | None
    estadoRegistro: str
    tiempoParqueo: int
    idVehiculo: int
    idCelda: int
    idOperario: int
