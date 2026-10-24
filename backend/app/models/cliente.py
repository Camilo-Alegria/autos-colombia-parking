from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    idCliente: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    documento: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    telefono: Mapped[str] = mapped_column(String(20), nullable=False)
    correo: Mapped[str] = mapped_column(String(120), nullable=False)

    vehiculos = relationship("Vehiculo", back_populates="cliente")
