from pydantic import BaseModel, ConfigDict, field_validator


class CeldaBase(BaseModel):
    codigo: str
    idTipo: int
    estado: str = "LIBRE"
    activo: bool = True


class CeldaCreate(CeldaBase):
    @field_validator("codigo")
    @classmethod
    def validar_codigo(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El código de la celda es obligatorio y no puede estar en blanco")
        return v.strip().upper()

    @field_validator("idTipo")
    @classmethod
    def validar_id_tipo(cls, v: int) -> int:
        if v is None or not isinstance(v, int) or v <= 0:
            raise ValueError("Debe seleccionar un tipo de vehículo válido")
        return v


class CeldaUpdate(BaseModel):
    codigo: str | None = None
    idTipo: int | None = None
    estado: str | None = None
    activo: bool | None = None

    @field_validator("codigo")
    @classmethod
    def validar_codigo(cls, v: str | None) -> str | None:
        if v is not None:
            if not v or not v.strip():
                raise ValueError("El código de la celda es obligatorio y no puede estar en blanco")
            return v.strip().upper()
        return v

    @field_validator("idTipo")
    @classmethod
    def validar_id_tipo(cls, v: int | None) -> int | None:
        if v is not None:
            if not isinstance(v, int) or v <= 0:
                raise ValueError("Debe seleccionar un tipo de vehículo válido")
        return v


class CeldaOut(CeldaBase):
    model_config = ConfigDict(from_attributes=True)

    idCelda: int


