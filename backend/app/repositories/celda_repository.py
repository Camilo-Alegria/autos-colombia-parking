from sqlalchemy.orm import Session

from app.models.celda import Celda


class CeldaRepository:
    def listar_celdas(self, db: Session, solo_activas: bool = True) -> list[Celda]:
        query = db.query(Celda)
        if solo_activas:
            query = query.filter(Celda.activo == True)  # noqa: E712
        return query.order_by(Celda.codigo.asc()).all()

    def listar_disponibles(self, db: Session, id_tipo: int | None = None) -> list[Celda]:
        query = db.query(Celda).filter(Celda.estado == "LIBRE", Celda.activo == True)  # noqa: E712
        if id_tipo is not None:
            query = query.filter(Celda.idTipo == id_tipo)
        return query.order_by(Celda.codigo.asc()).all()

    def obtener_por_id(self, db: Session, id_celda: int, for_update: bool = False) -> Celda | None:
        query = db.query(Celda).filter(Celda.idCelda == id_celda)
        if for_update:
            query = query.with_for_update()
        return query.first()

    def obtener_por_codigo(self, db: Session, codigo: str, for_update: bool = False) -> Celda | None:
        query = db.query(Celda).filter(Celda.codigo == codigo.strip().upper())
        if for_update:
            query = query.with_for_update()
        return query.first()

    def obtener_libre_por_tipo(self, db: Session, id_tipo: int, for_update: bool = False) -> Celda | None:
        query = db.query(Celda).filter(
            Celda.estado == "LIBRE",
            Celda.activo == True,  # noqa: E712
            Celda.idTipo == id_tipo,
        )
        if for_update:
            query = query.with_for_update()
        return query.first()

    def crear_celda(self, db: Session, data: dict) -> Celda:
        celda = Celda(**data)
        db.add(celda)
        db.commit()
        db.refresh(celda)
        return celda

    def actualizar_celda(self, db: Session, celda: Celda, data: dict) -> Celda:
        for campo, valor in data.items():
            if valor is not None:
                setattr(celda, campo, valor)
        db.commit()
        db.refresh(celda)
        return celda


celda_repo = CeldaRepository()
