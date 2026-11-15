from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.schemas.auditoria import AuditoriaOut
from app.services.auditoria_service import auditoria_service

router = APIRouter()


@router.get("/", response_model=list[AuditoriaOut])
def listar_auditorias(limite: int = 200, db: Session = Depends(get_db), _=Depends(require_admin)):
    return auditoria_service.listar_auditorias(db, limite=limite)
