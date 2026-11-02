from typing import Optional, List
from pydantic import BaseModel


class RolCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = ""
    color: Optional[str] = "#6161FF"
    alcance_proyectos: Optional[str] = "todos"  # "todos" o "uno"
    permisos: Optional[List[str]] = []


class RolUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    color: Optional[str] = None
    alcance_proyectos: Optional[str] = None  # "todos" o "uno"
    permisos: Optional[List[str]] = None

