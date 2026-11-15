from sqlalchemy.orm import Session

from app.models.registro_entrada_salida import RegistroEntradaSalida


class RegistroRepository:
    def obtener_por_id(self, db: Session, id_registro: int, for_update: bool = False) -> RegistroEntradaSalida | None:
        query = db.query(RegistroEntradaSalida).filter(RegistroEntradaSalida.idRegistro == id_registro)
        if for_update:
            query = query.with_for_update()
        return query.first()

    def obtener_activo_por_vehiculo(self, db: Session, id_vehiculo: int, for_update: bool = False) -> RegistroEntradaSalida | None:
        query = db.query(RegistroEntradaSalida).filter(
            RegistroEntradaSalida.idVehiculo == id_vehiculo,
            RegistroEntradaSalida.estadoRegistro == "ACTIVO",
        )
        if for_update:
            query = query.with_for_update()
        return query.first()

    def obtener_activo_por_celda(self, db: Session, id_celda: int, for_update: bool = False) -> RegistroEntradaSalida | None:
        query = db.query(RegistroEntradaSalida).filter(
            RegistroEntradaSalida.idCelda == id_celda,
            RegistroEntradaSalida.estadoRegistro == "ACTIVO",
        )
        if for_update:
            query = query.with_for_update()
        return query.first()

    def listar_activos(self, db: Session) -> list[RegistroEntradaSalida]:
        return (
            db.query(RegistroEntradaSalida)
            .filter(RegistroEntradaSalida.estadoRegistro == "ACTIVO")
            .all()
        )

    def listar_todos(self, db: Session) -> list[RegistroEntradaSalida]:
        return db.query(RegistroEntradaSalida).all()

    def crear_registro(self, db: Session, data: dict) -> RegistroEntradaSalida:
        registro = RegistroEntradaSalida(**data)
        db.add(registro)
        db.commit()
        db.refresh(registro)
        return registro

    def actualizar_registro(self, db: Session, registro: RegistroEntradaSalida, data: dict) -> RegistroEntradaSalida:
        for campo, valor in data.items():
            if valor is not None:
                setattr(registro, campo, valor)
        db.commit()
        db.refresh(registro)
        return registro


registro_repo = RegistroRepository()
