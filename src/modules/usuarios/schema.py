from typing import Optional
from pydantic import BaseModel, EmailStr


class UsuarioCreate(BaseModel):
    nombre: str
    email: str
    password: str
    rol_id: Optional[int] = None
    proyecto_id: Optional[int] = None
    cargo: Optional[str] = "Colaborador"
    activo: Optional[bool] = True


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    rol_id: Optional[int] = None
    proyecto_id: Optional[int] = None
    cargo: Optional[str] = None
    activo: Optional[bool] = None

