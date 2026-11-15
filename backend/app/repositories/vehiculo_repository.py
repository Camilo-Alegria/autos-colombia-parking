from sqlalchemy.orm import Session

from app.models.vehiculo import Vehiculo


class VehiculoRepository:
    def obtener_por_id(self, db: Session, id_vehiculo: int) -> Vehiculo | None:
        return db.get(Vehiculo, id_vehiculo)

    def obtener_por_placa(self, db: Session, placa: str) -> Vehiculo | None:
        return db.query(Vehiculo).filter(Vehiculo.placa == placa.strip().upper()).first()

    def listar_vehiculos(self, db: Session) -> list[Vehiculo]:
        return db.query(Vehiculo).all()

    def crear_vehiculo(self, db: Session, data: dict) -> Vehiculo:
        vehiculo = Vehiculo(**data)
        db.add(vehiculo)
        db.flush()
        return vehiculo

    def actualizar_vehiculo(self, db: Session, vehiculo: Vehiculo, data: dict) -> Vehiculo:
        for campo, valor in data.items():
            if valor is not None:
                setattr(vehiculo, campo, valor)
        db.commit()
        db.refresh(vehiculo)
        return vehiculo


vehiculo_repo = VehiculoRepository()
