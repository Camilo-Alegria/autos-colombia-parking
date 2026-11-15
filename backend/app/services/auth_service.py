from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.repositories.usuario_repository import usuario_repo
from app.schemas.auth import LoginRequest, TokenResponse


class AuthService:
    def autenticar_usuario(self, db: Session, request: LoginRequest) -> TokenResponse:
        user = usuario_repo.obtener_por_usuario(db, request.usuario)
        if not user or not user.activo or not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas o usuario inactivo",
            )
        token = create_access_token({
            "sub": str(user.id_usuario),
            "id_usuario": user.id_usuario,
            "usuario": user.usuario,
            "rol": user.rol,
            "nombre": user.nombre,
        })
        return TokenResponse(
            access_token=token,
            id_usuario=user.id_usuario,
            nombre=user.nombre,
            usuario=user.usuario,
            rol=user.rol,
        )

    def revocar_token(self, db: Session, token: str) -> None:
        from app.models.token_revocado import TokenRevocado
        existente = db.query(TokenRevocado).filter(TokenRevocado.token == token).first()
        if not existente:
            token_revocado = TokenRevocado(token=token)
            db.add(token_revocado)
            db.commit()

auth_service = AuthService()
