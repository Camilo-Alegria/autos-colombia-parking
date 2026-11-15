from datetime import datetime

from sqlalchemy import DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TokenRevocado(Base):
    __tablename__ = "tokens_revocados"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    token: Mapped[str] = mapped_column(Text, unique=True, index=True, nullable=False)
    fecha_revocacion: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
