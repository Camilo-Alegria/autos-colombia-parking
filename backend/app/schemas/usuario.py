from pydantic import BaseModel, ConfigDict, field_validator


class UsuarioBase(BaseModel):
    nombre: str
    documento: str
    usuario: str
    rol: str = "OPERADOR"
    activo: bool = True


class UsuarioCreate(UsuarioBase):
    password: str

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El campo Nombre completo es obligatorio")
        return v.strip()

    @field_validator("documento")
    @classmethod
    def validar_documento(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El campo Documento es obligatorio")
        return v.strip()

    @field_validator("usuario")
    @classmethod
    def validar_usuario(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El campo Usuario es obligatorio")
        return v.strip()

    @field_validator("rol")
    @classmethod
    def validar_rol(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El campo Rol es obligatorio")
        rol_limpio = v.strip().upper()
        if rol_limpio not in ("ADMINISTRADOR", "OPERADOR"):
            raise ValueError("El rol debe ser ADMINISTRADOR u OPERADOR")
        return rol_limpio

    @field_validator("password")
    @classmethod
    def validar_password(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El campo Contraseña es obligatorio")
        return v.strip()


class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    documento: str | None = None
    usuario: str | None = None
    password: str | None = None
    rol: str | None = None
    activo: bool | None = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, v: str | None) -> str | None:
        if v is not None:
            if not v.strip():
                raise ValueError("El campo Nombre completo es obligatorio")
            return v.strip()
        return v

    @field_validator("documento")
    @classmethod
    def validar_documento(cls, v: str | None) -> str | None:
        if v is not None:
            if not v.strip():
                raise ValueError("El campo Documento es obligatorio")
            return v.strip()
        return v

    @field_validator("usuario")
    @classmethod
    def validar_usuario(cls, v: str | None) -> str | None:
        if v is not None:
            if not v.strip():
                raise ValueError("El campo Usuario es obligatorio")
            return v.strip()
        return v

    @field_validator("rol")
    @classmethod
    def validar_rol(cls, v: str | None) -> str | None:
        if v is not None:
            if not v.strip():
                raise ValueError("El campo Rol es obligatorio")
            rol_limpio = v.strip().upper()
            if rol_limpio not in ("ADMINISTRADOR", "OPERADOR"):
                raise ValueError("El rol debe ser ADMINISTRADOR u OPERADOR")
            return rol_limpio
        return v

    @field_validator("password")
    @classmethod
    def validar_password(cls, v: str | None) -> str | None:
        if v is not None:
            if not v.strip():
                raise ValueError("El campo Contraseña es obligatorio")
            return v.strip()
        return v


class UsuarioOut(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)

    id_usuario: int


