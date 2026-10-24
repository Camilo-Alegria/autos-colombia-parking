from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ClienteResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idCliente: int
    nombre: str
    documento: str
    telefono: str
    correo: str


class TipoResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idTipo: int
    nombre: str
    tarifa: int


class VehiculoResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idVehiculo: int
    placa: str
    marca: str
    color: str
    idCliente: int
    idTipo: int


class RegistroResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idRegistro: int
    fechaIngreso: datetime
    fechaSalida: datetime | None
    estadoRegistro: str
    tiempoParqueo: int
    idVehiculo: int
    idCelda: int
    idOperario: int


class CeldaDetalleOut(BaseModel):
    idCelda: int
    codigo: str
    estado: str
    idTipo: int
    tipo: TipoResumen | None = None
    registro: RegistroResumen | None = None
    vehiculo: VehiculoResumen | None = None
    cliente: ClienteResumen | None = None


class DashboardOut(BaseModel):
    vehiculosRegistrados: int
    vehiculosIngresados: int
    celdasDisponibles: int
    defaultOperarioId: int | None = None
    celdas: list[CeldaDetalleOut]


class VehiculoDetalleOut(BaseModel):
    vehiculo: VehiculoResumen
    cliente: ClienteResumen
    tipo: TipoResumen
    celda: CeldaDetalleOut | None = None
    registroActivo: RegistroResumen | None = None


class SuscriptorCreate(BaseModel):
    nombre: str
    documento: str
    telefono: str
    correo: str
    placa: str
    marca: str
    color: str
    idTipo: int


class ReasignarCelda(BaseModel):
    idCelda: int
