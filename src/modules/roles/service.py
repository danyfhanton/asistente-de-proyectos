import json
from sqlalchemy.orm import Session
from src.models import Rol
from src.modules.roles.schema import RolCreate, RolUpdate


class RolesService:
    @staticmethod
    def get_roles(db: Session):
        return db.query(Rol).all()

    @staticmethod
    def get_rol(db: Session, rol_id: int):
        return db.query(Rol).filter(Rol.id == rol_id).first()

    @staticmethod
    def create_rol(db: Session, data: RolCreate):
        rol = Rol(
            nombre=data.nombre.strip(),
            descripcion=data.descripcion or "",
            color=data.color or "#6161FF",
            alcance_proyectos=data.alcance_proyectos or "todos",
            permisos=json.dumps(data.permisos or []),
        )
        db.add(rol)
        db.commit()
        db.refresh(rol)
        return rol

    @staticmethod
    def update_rol(db: Session, rol_id: int, data: RolUpdate):
        rol = db.query(Rol).filter(Rol.id == rol_id).first()
        if not rol:
            return None
        if data.nombre is not None:
            rol.nombre = data.nombre.strip()
        if data.descripcion is not None:
            rol.descripcion = data.descripcion
        if data.color is not None:
            rol.color = data.color
        if data.alcance_proyectos is not None:
            rol.alcance_proyectos = data.alcance_proyectos
        if data.permisos is not None:
            rol.permisos = json.dumps(data.permisos)
        db.commit()
        db.refresh(rol)
        return rol

    @staticmethod
    def delete_rol(db: Session, rol_id: int):
        rol = db.query(Rol).filter(Rol.id == rol_id).first()
        if not rol:
            return False
        db.delete(rol)
        db.commit()
        return True

