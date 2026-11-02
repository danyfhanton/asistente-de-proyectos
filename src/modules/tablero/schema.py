from typing import Optional
from datetime import date
from pydantic import BaseModel


class TareaCreate(BaseModel):
    grupo_id: int
    titulo: str
    descripcion: Optional[str] = ""
    estado: Optional[str] = "Por iniciar"
    prioridad: Optional[str] = "Media"
    responsable: Optional[str] = "Sin asignar"
    fecha_inicio: Optional[date] = None
    fecha_limite: Optional[date] = None
    puntos_historia: Optional[int] = 1
    tipo_tarea: Optional[str] = "Tarea"
    sprint_id: Optional[int] = None


class TareaUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[str] = None
    prioridad: Optional[str] = None
    responsable: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_limite: Optional[date] = None
    puntos_historia: Optional[int] = None
    tipo_tarea: Optional[str] = None
    grupo_id: Optional[int] = None
    sprint_id: Optional[int] = None
    orden: Optional[int] = None


class TareaMover(BaseModel):
    grupo_id: int
    nuevo_orden: Optional[int] = 0


class FechaUpdate(BaseModel):
    fecha_limite: Optional[date] = None
    fecha_inicio: Optional[date] = None


class EstadoUpdate(BaseModel):
    estado: str


class GrupoCreate(BaseModel):
    proyecto_id: int
    titulo: str
    color: Optional[str] = "#579BFC"


class GrupoUpdate(BaseModel):
    titulo: Optional[str] = None
    color: Optional[str] = None
    colapsado: Optional[bool] = None


class ProyectoCreate(BaseModel):
    nombre: str
    clave: Optional[str] = "PRJ"
    descripcion: Optional[str] = ""
    color: Optional[str] = "#6161FF"


class SubtareaCreate(BaseModel):
    titulo: str


class ComentarioCreate(BaseModel):
    autor: Optional[str] = "Usuario"
    contenido: str

