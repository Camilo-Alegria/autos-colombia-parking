from sqlalchemy.orm import Session

from app.models.historial_auditoria import HistorialAuditoria
from app.repositories.auditoria_repository import auditoria_repo


class AuditoriaService:
    def registrar_accion(
        self,
        db: Session,
        accion: str,
        detalles: str | None = None,
        usuario=None,
        ip: str | None = None,
    ) -> HistorialAuditoria:
        u_id = usuario.id_usuario if usuario and hasattr(usuario, "id_usuario") else None
        u_nombre = usuario.nombre if usuario and hasattr(usuario, "nombre") else None
        return auditoria_repo.registrar_auditoria(
            db,
            accion=accion,
            detalles=detalles,
            usuario_id=u_id,
            usuario_nombre=u_nombre,
            ip=ip,
        )

    def listar_auditorias(self, db: Session, limite: int = 200) -> list[HistorialAuditoria]:
        return auditoria_repo.listar_auditorias(db, limite=limite)


auditoria_service = AuditoriaService()
