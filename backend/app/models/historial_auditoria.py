from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class HistorialAuditoria(Base):
    __tablename__ = "historial_auditoria"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id_usuario"), nullable=True)
    usuario_nombre: Mapped[str | None] = mapped_column(String(120), nullable=True)
    accion: Mapped[str] = mapped_column(String(80), nullable=False)
    detalles: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip: Mapped[str | None] = mapped_column(String(50), nullable=True)

    usuario = relationship("Usuario", back_populates="auditorias")
