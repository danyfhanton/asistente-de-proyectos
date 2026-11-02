from typing import Optional
from datetime import date
from pydantic import BaseModel


class SprintCreate(BaseModel):
    proyecto_id: int
    nombre: str
    objetivo: Optional[str] = ""
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None


class SprintUpdate(BaseModel):
    nombre: Optional[str] = None
    objetivo: Optional[str] = None
    estado: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None


class MoverSprint(BaseModel):
    sprint_id: Optional[int] = None  # None para mover a Backlog general

