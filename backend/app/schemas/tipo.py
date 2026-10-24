from pydantic import BaseModel, ConfigDict


class TipoBase(BaseModel):
    nombre: str
    descripcion: str | None = None
    tarifa: int = 0


class TipoCreate(TipoBase):
    pass


class TipoUpdate(TipoBase):
    pass


class TipoOut(TipoBase):
    model_config = ConfigDict(from_attributes=True)

    idTipo: int
