from datetime import datetime
from sqlalchemy.orm import Session

from app.models.historial_auditoria import HistorialAuditoria


class AuditoriaRepository:
    def registrar_auditoria(
        self,
        db: Session,
        accion: str,
        detalles: str | None = None,
        usuario_id: int | None = None,
        usuario_nombre: str | None = None,
        ip: str | None = None,
    ) -> HistorialAuditoria:
        log = HistorialAuditoria(
            fecha_hora=datetime.now(),
            usuario_id=usuario_id,
            usuario_nombre=usuario_nombre,
            accion=accion,
            detalles=detalles,
            ip=ip,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    def listar_auditorias(self, db: Session, limite: int = 200) -> list[HistorialAuditoria]:
        return (
            db.query(HistorialAuditoria)
            .order_by(HistorialAuditoria.fecha_hora.desc())
            .limit(limite)
            .all()
        )


auditoria_repo = AuditoriaRepository()
