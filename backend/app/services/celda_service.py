from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.websocket_manager import ws_manager
from app.models.celda import Celda
from app.models.registro_entrada_salida import RegistroEntradaSalida
from app.models.tipo import Tipo
from app.repositories.celda_repository import celda_repo
from app.schemas.celda import CeldaCreate, CeldaUpdate
from app.services.auditoria_service import auditoria_service


class CeldaService:
    def listar_celdas(self, db: Session) -> list[Celda]:
        return celda_repo.listar_celdas(db, solo_activas=False)

    def listar_disponibles(self, db: Session, id_tipo: int | None = None) -> list[Celda]:
        return celda_repo.listar_disponibles(db, id_tipo=id_tipo)

    async def crear_celda(self, db: Session, payload: CeldaCreate, current_user, ip: str | None = None) -> Celda:
        if not db.get(Tipo, payload.idTipo):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo no encontrado")
        if celda_repo.obtener_por_codigo(db, payload.codigo):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El código de celda ya existe")

        try:
            celda = celda_repo.crear_celda(db, payload.model_dump())
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El código de celda ya existe")

        auditoria_service.registrar_accion(
            db,
            accion="CREAR_CELDA",
            detalles=f"Creada celda {celda.codigo}",
            usuario=current_user,
            ip=ip,
        )
        await ws_manager.broadcast({"event": "celda_actualizada", "codigo": celda.codigo})
        return celda

    async def actualizar_celda(self, db: Session, id_celda: int, payload: CeldaUpdate, current_user, ip: str | None = None) -> Celda:
        celda = celda_repo.obtener_por_id(db, id_celda)
        if not celda:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Celda no encontrada")

        data = payload.model_dump(exclude_unset=True)
        if "idTipo" in data and not db.get(Tipo, data["idTipo"]):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo no encontrado")

        if "codigo" in data and data["codigo"] is not None:
            codigo_normalizado = data["codigo"].strip().upper()
            existente = db.query(Celda).filter(
                Celda.codigo == codigo_normalizado,
                Celda.idCelda != id_celda
            ).first()
            if existente:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El código de celda ya existe")
            data["codigo"] = codigo_normalizado

        try:
            updated = celda_repo.actualizar_celda(db, celda, data)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El código de celda ya existe")

        auditoria_service.registrar_accion(
            db,
            accion="ACTUALIZAR_CELDA",
            detalles=f"Actualizada celda {updated.codigo}",
            usuario=current_user,
            ip=ip,
        )
        await ws_manager.broadcast({"event": "celda_actualizada", "codigo": updated.codigo})
        return updated

    async def eliminar_celda(self, db: Session, id_celda: int, usuario_actual, ip: str | None = None) -> None:
        celda = celda_repo.obtener_por_id(db, id_celda)
        if not celda:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Celda no encontrada")
        if celda.estado != "LIBRE":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede eliminar una celda que está OCUPADA",
            )
        tiene_registros = (
            db.query(RegistroEntradaSalida)
            .filter(RegistroEntradaSalida.idCelda == id_celda)
            .first()
        )
        if tiene_registros:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede eliminar la celda porque posee historial en registros de entrada y salida",
            )

        codigo_celda = celda.codigo
        db.delete(celda)
        db.commit()

        auditoria_service.registrar_accion(
            db,
            accion="ELIMINAR_CELDA",
            detalles=f"Eliminada celda {codigo_celda}",
            usuario=usuario_actual,
            ip=ip,
        )
        await ws_manager.broadcast({"event": "celda_actualizada", "codigo": codigo_celda})


celda_service = CeldaService()

