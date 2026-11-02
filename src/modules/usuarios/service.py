import random
from sqlalchemy.orm import Session
from src.models import Usuario, Rol
from src.core.security import hash_password
from src.modules.usuarios.schema import UsuarioCreate, UsuarioUpdate

AVATAR_COLORS = ["#6161FF", "#00C875", "#FDAB3D", "#E2445C", "#A25DDC", "#00D2D2", "#FF5AC4"]


class UsuariosService:
    @staticmethod
    def get_usuarios(db: Session):
        return db.query(Usuario).order_by(Usuario.id).all()

    @staticmethod
    def get_usuario(db: Session, user_id: int):
        return db.query(Usuario).filter(Usuario.id == user_id).first()

    @staticmethod
    def create_usuario(db: Session, data: UsuarioCreate):
        # Verificar email duplicado
        existente = db.query(Usuario).filter(Usuario.email == data.email.strip().lower()).first()
        if existente:
            return None

        color = random.choice(AVATAR_COLORS)
        nuevo = Usuario(
            nombre=data.nombre.strip(),
            email=data.email.strip().lower(),
            password_hash=hash_password(data.password),
            rol_id=data.rol_id,
            proyecto_id=data.proyecto_id,
            cargo=data.cargo or "Colaborador",
            activo=data.activo if data.activo is not None else True,
            avatar_color=color,
        )
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo

    @staticmethod
    def update_usuario(db: Session, user_id: int, data: UsuarioUpdate):
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            return None

        if data.nombre is not None:
            user.nombre = data.nombre.strip()
        if data.email is not None:
            user.email = data.email.strip().lower()
        if data.password:
            user.password_hash = hash_password(data.password)
        if data.rol_id is not None:
            user.rol_id = data.rol_id
        if "proyecto_id" in data.model_dump(exclude_unset=True):
            user.proyecto_id = data.proyecto_id
        if data.cargo is not None:
            user.cargo = data.cargo
        if data.activo is not None:
            user.activo = data.activo

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def toggle_activo(db: Session, user_id: int):
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            return None
        user.activo = not user.activo
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_usuario(db: Session, user_id: int):
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            return False
        db.delete(user)
        db.commit()
        return True

