from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Operario(Base):
    __tablename__ = "operarios"

    idOperario: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    documento: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    usuario: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)

    registros = relationship("RegistroEntradaSalida", back_populates="operario")
