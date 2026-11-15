from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, security_scheme
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.usuario import UsuarioOut
from app.services.auth_service import auth_service

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.autenticar_usuario(db, payload)


@router.get("/me", response_model=UsuarioOut)
def obtener_yo(current_user=Depends(get_current_user)):
    return current_user


@router.post("/logout")
def logout(
    auth: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if auth and auth.credentials:
        auth_service.revocar_token(db, auth.credentials)
    return {"message": "Sesión cerrada correctamente"}
