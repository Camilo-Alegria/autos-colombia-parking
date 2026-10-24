from pydantic import BaseModel, ConfigDict


class OperarioBase(BaseModel):
    nombre: str
    documento: str
    usuario: str


class OperarioCreate(OperarioBase):
    pass


class OperarioUpdate(OperarioBase):
    pass


class OperarioOut(OperarioBase):
    model_config = ConfigDict(from_attributes=True)

    idOperario: int
