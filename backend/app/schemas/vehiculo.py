from pydantic import BaseModel, ConfigDict


class VehiculoBase(BaseModel):
    placa: str
    marca: str
    color: str
    idCliente: int
    idTipo: int


class VehiculoCreate(VehiculoBase):
    pass


class VehiculoUpdate(VehiculoBase):
    pass


class VehiculoOut(VehiculoBase):
    model_config = ConfigDict(from_attributes=True)

    idVehiculo: int
