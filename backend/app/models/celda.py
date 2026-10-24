from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Celda(Base):
    __tablename__ = "celdas"

    idCelda: Mapped[int] = mapped_column(primary_key=True, index=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="LIBRE")
    idTipo: Mapped[int] = mapped_column(ForeignKey("tipos.idTipo"), nullable=False)

    tipo = relationship("Tipo", back_populates="celdas")
    registros = relationship("RegistroEntradaSalida", back_populates="celda")
