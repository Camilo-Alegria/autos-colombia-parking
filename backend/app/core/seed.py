from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.core.database import Base, engine
from app.core.security import hash_password
from app.models.celda import Celda
from app.models.tipo import Tipo
from app.models.usuario import Usuario

TARIFA_CARRO = 250_000
TARIFA_MOTO = 100_000


from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.core.database import Base, engine
from app.core.security import hash_password
from app.models.celda import Celda
from app.models.tipo import Tipo
from app.models.usuario import Usuario

TARIFA_CARRO = 250_000
TARIFA_MOTO = 100_000


def ensure_schema() -> None:
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    with engine.begin() as conexion:
        if "tipos" in tables:
            cols = {col["name"] for col in inspector.get_columns("tipos")}
            if "tarifa" not in cols:
                conexion.execute(text("ALTER TABLE tipos ADD COLUMN tarifa INTEGER NOT NULL DEFAULT 0"))

        if "vehiculos" in tables:
            cols = {col["name"] for col in inspector.get_columns("vehiculos")}
            if "modelo" not in cols:
                conexion.execute(text("ALTER TABLE vehiculos ADD COLUMN modelo VARCHAR(40) NOT NULL DEFAULT ''"))
            if "estado_pago" not in cols:
                conexion.execute(text("ALTER TABLE vehiculos ADD COLUMN estado_pago VARCHAR(20) NOT NULL DEFAULT 'AL_DIA'"))
            if "dia_corte" not in cols:
                conexion.execute(text("ALTER TABLE vehiculos ADD COLUMN dia_corte INTEGER"))
            if "fecha_vencimiento" not in cols:
                conexion.execute(text("ALTER TABLE vehiculos ADD COLUMN fecha_vencimiento DATE"))
            if "id_usuario_cliente" not in cols:
                conexion.execute(text("ALTER TABLE vehiculos ADD COLUMN id_usuario_cliente INTEGER REFERENCES usuarios(id_usuario)"))

        if "celdas" in tables:
            cols = {col["name"] for col in inspector.get_columns("celdas")}
            if "activo" not in cols:
                conexion.execute(text("ALTER TABLE celdas ADD COLUMN activo BOOLEAN NOT NULL DEFAULT TRUE"))

        if "usuarios" in tables:
            cols = {col["name"] for col in inspector.get_columns("usuarios")}
            # Ensure rol column supports CLIENTE (already a String column)



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

    # Seed Admin User
    admin = db.query(Usuario).filter(Usuario.usuario == "admin").first()
    if not admin:
        admin = Usuario(
            nombre="Administrador General",
            documento="1111111111",
            usuario="admin",
            password_hash=hash_password("admin123"),
            rol="ADMINISTRADOR",
            activo=True,
        )
        db.add(admin)

    # Seed Operator User
    operador = db.query(Usuario).filter(Usuario.usuario == "operador").first()
    if not operador:
        operador = Usuario(
            nombre="Operador Turno 1",
            documento="2222222222",
            usuario="operador",
            password_hash=hash_password("operador123"),
            rol="OPERADOR",
            activo=True,
        )
        db.add(operador)

    db.commit()

    existentes = {celda.codigo for celda in db.query(Celda).all()}
    nuevas: list[Celda] = []
    for numero in range(1, 71):
        codigo = f"C{numero:02d}"
        if codigo not in existentes:
            nuevas.append(Celda(codigo=codigo, estado="LIBRE", activo=True, idTipo=carro.idTipo))
    for numero in range(1, 11):
        codigo = f"M{numero:02d}"
        if codigo not in existentes:
            nuevas.append(Celda(codigo=codigo, estado="LIBRE", activo=True, idTipo=moto.idTipo))
    if nuevas:
        db.add_all(nuevas)

    db.commit()

