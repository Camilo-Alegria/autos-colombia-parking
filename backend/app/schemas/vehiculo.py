from pydantic import BaseModel, ConfigDict


class VehiculoBase(BaseModel):
    placa: str
    marca: str
    modelo: str = ""
    color: str
    estado_pago: str = "AL_DIA"
    idCliente: int
    idTipo: int


class VehiculoCreate(VehiculoBase):
    pass


class VehiculoUpdate(BaseModel):
    placa: str | None = None
    marca: str | None = None
    modelo: str | None = None
    color: str | None = None
    estado_pago: str | None = None
    idCliente: int | None = None
    idTipo: int | None = None


class VehiculoOut(VehiculoBase):
    model_config = ConfigDict(from_attributes=True)

    idVehiculo: int

