from pydantic import BaseModel, ConfigDict


class ClienteBase(BaseModel):
    nombre: str
    documento: str
    telefono: str
    correo: str


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(ClienteBase):
    pass


class ClienteOut(ClienteBase):
    model_config = ConfigDict(from_attributes=True)

    idCliente: int
