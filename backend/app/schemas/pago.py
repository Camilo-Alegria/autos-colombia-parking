from datetime import date, datetime
from pydantic import BaseModel, Field


class VehiculoClienteCreate(BaseModel):
    cedula: str = Field(..., min_length=1, max_length=30)
    nombre: str = Field(..., min_length=1, max_length=120)
    telefono: str = Field(..., min_length=1, max_length=20)
    password: str = Field(..., min_length=1, max_length=100)
    placa: str = Field(..., min_length=1, max_length=10)
    idTipo: int
    marca: str = Field(..., min_length=1, max_length=60)
    modelo: str = Field(..., min_length=1, max_length=40)
    color: str = Field(..., min_length=1, max_length=40)


class PagoPresencialCreate(BaseModel):
    placa: str = Field(..., min_length=1, max_length=10)
    id_operario: int | None = None


class PagoOut(BaseModel):
    id_pago: int
    id_vehiculo: int
    monto: int
    metodo_pago: str
    referencia_pasarela: str | None = None
    estado: str
    fecha_pago: datetime

    class Config:
        from_attributes = True


class VehiculoEstadoCuentaOut(BaseModel):
    idVehiculo: int
    placa: str
    marca: str
    modelo: str
    color: str
    dia_corte: int | None = None
    fecha_vencimiento: date | None = None
    estado_pago: str
    estado_semaforo: str
    tarifa: int
    historial_pagos: list[PagoOut] = []

    class Config:
        from_attributes = True


class ClienteEstadoCuentaOut(BaseModel):
    cedula: str
    nombre: str
    vehiculos: list[VehiculoEstadoCuentaOut] = []
