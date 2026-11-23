from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    documento: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    usuario: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(30), nullable=False, default="OPERADOR") # "ADMINISTRADOR", "OPERADOR", "CLIENTE"
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    registros = relationship("RegistroEntradaSalida", back_populates="usuario")
    auditorias = relationship("HistorialAuditoria", back_populates="usuario")
    vehiculos_cliente = relationship("Vehiculo", back_populates="cliente_usuario")

