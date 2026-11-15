from sqlalchemy.orm import Session

from app.models.usuario import Usuario


class UsuarioRepository:
    def obtener_por_usuario(self, db: Session, usuario: str) -> Usuario | None:
        return db.query(Usuario).filter(Usuario.usuario == usuario.strip()).first()

    def obtener_por_id(self, db: Session, id_usuario: int) -> Usuario | None:
        return db.get(Usuario, id_usuario)

    def obtener_por_documento(self, db: Session, documento: str) -> Usuario | None:
        return db.query(Usuario).filter(Usuario.documento == documento.strip()).first()

    def listar_usuarios(self, db: Session) -> list[Usuario]:
        return db.query(Usuario).order_by(Usuario.id_usuario.asc()).all()

    def crear_usuario(self, db: Session, data: dict) -> Usuario:
        usuario = Usuario(**data)
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario

    def actualizar_usuario(self, db: Session, usuario: Usuario, data: dict) -> Usuario:
        for campo, valor in data.items():
            if valor is not None:
                setattr(usuario, campo, valor)
        db.commit()
        db.refresh(usuario)
        return usuario

    def desactivar_usuario(self, db: Session, usuario: Usuario) -> Usuario:
        usuario.activo = False
        db.commit()
        db.refresh(usuario)
        return usuario


usuario_repo = UsuarioRepository()
