from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.repositories.cliente_repository import cliente_repo
from app.schemas.cliente import ClienteUpdate
from app.services.auditoria_service import auditoria_service


class ClienteService:
    def listar_clientes(self, db: Session) -> list[Cliente]:
        return cliente_repo.listar_clientes(db)

    def actualizar_cliente(self, db: Session, id_cliente: int, payload: ClienteUpdate, current_user, ip: str | None = None) -> Cliente:
        cliente = cliente_repo.obtener_por_id(db, id_cliente)
        if not cliente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
        updated = cliente_repo.actualizar_cliente(db, cliente, payload.model_dump())
        auditoria_service.registrar_accion(
            db,
            accion="ACTUALIZAR_CLIENTE",
            detalles=f"Actualizado propietario {updated.nombre} ({updated.documento})",
            usuario=current_user,
            ip=ip,
        )
        return updated


cliente_service = ClienteService()
