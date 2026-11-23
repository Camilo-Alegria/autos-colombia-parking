from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Pago(Base):
    __tablename__ = "pagos"

    id_pago: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_vehiculo: Mapped[int] = mapped_column(ForeignKey("vehiculos.idVehiculo"), nullable=False)
    monto: Mapped[int] = mapped_column(Integer, nullable=False)
    metodo_pago: Mapped[str] = mapped_column(String(30), nullable=False)  # "ONLINE" o "PRESENCIAL"
    referencia_pasarela: Mapped[str | None] = mapped_column(String(100), nullable=True)
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default="APROBADO")  # "APROBADO" o "RECHAZADO"
    fecha_pago: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)

    vehiculo = relationship("Vehiculo", back_populates="pagos")
