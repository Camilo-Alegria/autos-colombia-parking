from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Tipo(Base):
    __tablename__ = "tipos"

    idTipo: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    descripcion: Mapped[str] = mapped_column(String(255), nullable=True)
    tarifa: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    vehiculos = relationship("Vehiculo", back_populates="tipo")
    celdas = relationship("Celda", back_populates="tipo")
