from datetime import date
from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Vehiculo(Base):
    __tablename__ = "vehiculos"

    idVehiculo: Mapped[int] = mapped_column(primary_key=True, index=True)
    placa: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    marca: Mapped[str] = mapped_column(String(60), nullable=False)
    modelo: Mapped[str] = mapped_column(String(40), nullable=False, default="")
    color: Mapped[str] = mapped_column(String(40), nullable=False)
    estado_pago: Mapped[str] = mapped_column(String(20), nullable=False, default="AL_DIA")
    dia_corte: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fecha_vencimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    id_usuario_cliente: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id_usuario"), nullable=True)
    idCliente: Mapped[int] = mapped_column(ForeignKey("clientes.idCliente"), nullable=False)
    idTipo: Mapped[int] = mapped_column(ForeignKey("tipos.idTipo"), nullable=False)

    cliente = relationship("Cliente", back_populates="vehiculos")
    cliente_usuario = relationship("Usuario", back_populates="vehiculos_cliente")
    tipo = relationship("Tipo", back_populates="vehiculos")
    registros = relationship("RegistroEntradaSalida", back_populates="vehiculo")
    pagos = relationship("Pago", back_populates="vehiculo", cascade="all, delete-orphan")


