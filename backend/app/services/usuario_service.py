from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.usuario import Usuario
from app.repositories.usuario_repository import usuario_repo
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.services.auditoria_service import auditoria_service


class UsuarioService:
    def listar_usuarios(self, db: Session) -> list[Usuario]:
        return usuario_repo.listar_usuarios(db)

    def crear_usuario(self, db: Session, payload: UsuarioCreate, current_user, ip: str | None = None) -> Usuario:
        if usuario_repo.obtener_por_usuario(db, payload.usuario):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El nombre de usuario ya existe")
        if usuario_repo.obtener_por_documento(db, payload.documento):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El documento ya existe")

        data = payload.model_dump(exclude={"password"})
        data["password_hash"] = hash_password(payload.password)
        usuario = usuario_repo.crear_usuario(db, data)
        auditoria_service.registrar_accion(
            db,
            accion="CREAR_USUARIO",
            detalles=f"Creado usuario {usuario.usuario} ({usuario.rol})",
            usuario=current_user,
            ip=ip,
        )
        return usuario

    def actualizar_usuario(self, db: Session, id_usuario: int, payload: UsuarioUpdate, current_user, ip: str | None = None) -> Usuario:
        usuario = usuario_repo.obtener_por_id(db, id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

        data = payload.model_dump(exclude_unset=True, exclude={"password"})
        if "password" in payload.model_dump(exclude_unset=True) and payload.password:
            data["password_hash"] = hash_password(payload.password)

        if "usuario" in data and data["usuario"] != usuario.usuario:
            if usuario_repo.obtener_por_usuario(db, data["usuario"]):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El nombre de usuario ya existe")

        updated = usuario_repo.actualizar_usuario(db, usuario, data)
        auditoria_service.registrar_accion(
            db,
            accion="ACTUALIZAR_USUARIO",
            detalles=f"Actualizado usuario {updated.usuario}",
            usuario=current_user,
            ip=ip,
        )
        return updated

    def desactivar_usuario(self, db: Session, id_usuario: int, current_user, ip: str | None = None) -> Usuario:
        usuario = usuario_repo.obtener_por_id(db, id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        deactivated = usuario_repo.desactivar_usuario(db, usuario)
        auditoria_service.registrar_accion(
            db,
            accion="DESACTIVAR_USUARIO",
            detalles=f"Borrado lógico (inactivación) del usuario {deactivated.usuario}",
            usuario=current_user,
            ip=ip,
        )
        return deactivated


usuario_service = UsuarioService()
