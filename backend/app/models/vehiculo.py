from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Vehiculo(Base):
    __tablename__ = "vehiculos"

    idVehiculo: Mapped[int] = mapped_column(primary_key=True, index=True)
    placa: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    marca: Mapped[str] = mapped_column(String(60), nullable=False)
    color: Mapped[str] = mapped_column(String(40), nullable=False)
    idCliente: Mapped[int] = mapped_column(ForeignKey("clientes.idCliente"), nullable=False)
    idTipo: Mapped[int] = mapped_column(ForeignKey("tipos.idTipo"), nullable=False)

    cliente = relationship("Cliente", back_populates="vehiculos")
    tipo = relationship("Tipo", back_populates="vehiculos")
    registros = relationship("RegistroEntradaSalida", back_populates="vehiculo")
