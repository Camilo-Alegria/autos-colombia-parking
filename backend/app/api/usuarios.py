from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.schemas.usuario import UsuarioCreate, UsuarioOut, UsuarioUpdate
from app.services.usuario_service import usuario_service

router = APIRouter()


@router.get("/", response_model=list[UsuarioOut])
def listar_usuarios(db: Session = Depends(get_db), _=Depends(require_admin)):
    return usuario_service.listar_usuarios(db)


@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear_usuario(payload: UsuarioCreate, request: Request, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    ip = request.client.host if request.client else None
    return usuario_service.crear_usuario(db, payload, current_user, ip)


@router.put("/{id_usuario}", response_model=UsuarioOut)
def actualizar_usuario(id_usuario: int, payload: UsuarioUpdate, request: Request, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    ip = request.client.host if request.client else None
    return usuario_service.actualizar_usuario(db, id_usuario, payload, current_user, ip)


@router.delete("/{id_usuario}", response_model=UsuarioOut)
def desactivar_usuario(id_usuario: int, request: Request, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    ip = request.client.host if request.client else None
    return usuario_service.desactivar_usuario(db, id_usuario, current_user, ip)
