from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.core.database import engine
from app.models.celda import Celda
from app.models.operario import Operario
from app.models.tipo import Tipo

TARIFA_CARRO = 250_000
TARIFA_MOTO = 100_000


def ensure_schema() -> None:
    inspector = inspect(engine)
    if "tipos" not in inspector.get_table_names():
        return
    columnas = {col["name"] for col in inspector.get_columns("tipos")}
    if "tarifa" not in columnas:
        with engine.begin() as conexion:
            conexion.execute(text("ALTER TABLE tipos ADD COLUMN tarifa INTEGER NOT NULL DEFAULT 0"))


def seed_datos_iniciales(db: Session) -> None:
    carro = db.query(Tipo).filter(Tipo.nombre == "Carro").first()
    if not carro:
        carro = Tipo(nombre="Carro", descripcion="Vehículo liviano", tarifa=TARIFA_CARRO)
        db.add(carro)
        db.flush()
    else:
        carro.tarifa = TARIFA_CARRO
        if not carro.descripcion:
            carro.descripcion = "Vehículo liviano"

    moto = db.query(Tipo).filter(Tipo.nombre == "Moto").first()
    if not moto:
        moto = Tipo(nombre="Moto", descripcion="Motocicleta", tarifa=TARIFA_MOTO)
        db.add(moto)
        db.flush()
    else:
        moto.tarifa = TARIFA_MOTO
        if not moto.descripcion:
            moto.descripcion = "Motocicleta"

    if not db.query(Operario).first():
        db.add(
            Operario(
                nombre="Operario Sistema",
                documento="0000000000",
                usuario="sistema",
            )
        )

    existentes = {celda.codigo for celda in db.query(Celda).all()}
    nuevas: list[Celda] = []
    for numero in range(1, 71):
        codigo = f"C{numero:02d}"
        if codigo not in existentes:
            nuevas.append(Celda(codigo=codigo, estado="LIBRE", idTipo=carro.idTipo))
    for numero in range(1, 11):
        codigo = f"M{numero:02d}"
        if codigo not in existentes:
            nuevas.append(Celda(codigo=codigo, estado="LIBRE", idTipo=moto.idTipo))
    if nuevas:
        db.add_all(nuevas)

    db.commit()
