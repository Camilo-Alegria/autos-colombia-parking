from sqlalchemy.orm import Session

from app.models.cliente import Cliente


class ClienteRepository:
    def obtener_por_id(self, db: Session, id_cliente: int) -> Cliente | None:
        return db.get(Cliente, id_cliente)

    def obtener_por_documento(self, db: Session, documento: str) -> Cliente | None:
        return db.query(Cliente).filter(Cliente.documento == documento.strip()).first()

    def listar_clientes(self, db: Session) -> list[Cliente]:
        return db.query(Cliente).all()

    def crear_cliente(self, db: Session, data: dict) -> Cliente:
        cliente = Cliente(**data)
        db.add(cliente)
        db.flush()
        return cliente

    def actualizar_cliente(self, db: Session, cliente: Cliente, data: dict) -> Cliente:
        for campo, valor in data.items():
            if valor is not None:
                setattr(cliente, campo, valor)
        db.commit()
        db.refresh(cliente)
        return cliente


cliente_repo = ClienteRepository()
