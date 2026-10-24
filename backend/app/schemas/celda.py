from pydantic import BaseModel, ConfigDict


class CeldaBase(BaseModel):
    codigo: str
    idTipo: int
    estado: str = "LIBRE"


class CeldaCreate(CeldaBase):
    pass


class CeldaUpdate(BaseModel):
    codigo: str | None = None
    idTipo: int | None = None
    estado: str | None = None


class CeldaOut(CeldaBase):
    model_config = ConfigDict(from_attributes=True)

    idCelda: int
