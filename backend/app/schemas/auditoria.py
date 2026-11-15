from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditoriaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha_hora: datetime
    usuario_id: int | None = None
    usuario_nombre: str | None = None
    accion: str
    detalles: str | None = None
    ip: str | None = None
