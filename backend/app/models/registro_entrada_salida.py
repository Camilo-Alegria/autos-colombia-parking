from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RegistroEntradaSalida(Base):
    __tablename__ = "registros_entrada_salida"

    idRegistro: Mapped[int] = mapped_column(primary_key=True, index=True)
    fechaIngreso: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fechaSalida: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    estadoRegistro: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVO")
    tiempoParqueo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    idVehiculo: Mapped[int] = mapped_column(
        ForeignKey("vehiculos.idVehiculo"), nullable=False
    )
    idCelda: Mapped[int] = mapped_column(ForeignKey("celdas.idCelda"), nullable=False)
    idOperario: Mapped[int] = mapped_column(
        ForeignKey("operarios.idOperario"), nullable=False
    )

    vehiculo = relationship("Vehiculo", back_populates="registros")
    celda = relationship("Celda", back_populates="registros")
    operario = relationship("Operario", back_populates="registros")
