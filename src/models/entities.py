from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from src.core.database import Base


class Rol(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(80), unique=True, nullable=False)
    descripcion = Column(String(250), default="")
    color = Column(String(20), default="#6161FF")
    alcance_proyectos = Column(String(20), default="todos")  # 'todos' o 'uno'
    permisos = Column(Text, default="[]")  # Lista de permisos en formato JSON
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    usuarios = relationship("Usuario", back_populates="rol", cascade="all, delete-orphan")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    rol_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"), nullable=True)
    cargo = Column(String(100), default="Colaborador")
    activo = Column(Boolean, default=True)
    avatar_color = Column(String(20), default="#6161FF")
    ultimo_acceso = Column(DateTime, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    rol = relationship("Rol", back_populates="usuarios")
    proyecto_asignado = relationship("Proyecto", foreign_keys=[proyecto_id])


class Proyecto(Base):
    __tablename__ = "proyectos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    clave = Column(String(10), default="PRJ")
    descripcion = Column(Text, default="")
    color = Column(String(20), default="#6161FF")  # Color estilo Monday
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    grupos = relationship("Grupo", back_populates="proyecto", cascade="all, delete-orphan", order_by="Grupo.orden")
    sprints = relationship("Sprint", back_populates="proyecto", cascade="all, delete-orphan", order_by="Sprint.id.desc()")


class Sprint(Base):
    __tablename__ = "sprints"

    id = Column(Integer, primary_key=True, index=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
    objetivo = Column(Text, default="")
    estado = Column(String(30), default="Planificado")  # Planificado, Activo, Completado
    fecha_inicio = Column(Date, nullable=True)
    fecha_fin = Column(Date, nullable=True)

    proyecto = relationship("Proyecto", back_populates="sprints")
    tareas = relationship("Tarea", back_populates="sprint")


class Grupo(Base):
    __tablename__ = "grupos"

    id = Column(Integer, primary_key=True, index=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"), nullable=False)
    titulo = Column(String(100), nullable=False)
    color = Column(String(20), default="#579BFC")  # Monday pastel/vivid header color
    orden = Column(Integer, default=0)
    colapsado = Column(Boolean, default=False)

    proyecto = relationship("Proyecto", back_populates="grupos")
    tareas = relationship("Tarea", back_populates="grupo", cascade="all, delete-orphan", order_by="Tarea.orden")


class Tarea(Base):
    __tablename__ = "tareas"

    id = Column(Integer, primary_key=True, index=True)
    grupo_id = Column(Integer, ForeignKey("grupos.id"), nullable=False)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=True)

    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, default="")
    estado = Column(String(40), default="Por iniciar")  # Por iniciar, En curso, En espera, Bloqueado, Listo
    prioridad = Column(String(30), default="Media")     # Baja, Media, Alta, Crítica
    responsable = Column(String(100), default="Sin asignar")
    fecha_inicio = Column(Date, nullable=True)
    fecha_limite = Column(Date, nullable=True)
    puntos_historia = Column(Integer, default=1)
    tipo_tarea = Column(String(30), default="Tarea")    # Tarea, Historia, Bug, Mejora
    orden = Column(Integer, default=0)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    grupo = relationship("Grupo", back_populates="tareas")
    sprint = relationship("Sprint", back_populates="tareas")
    subtareas = relationship("Subtarea", back_populates="tarea", cascade="all, delete-orphan", order_by="Subtarea.orden")
    comentarios = relationship("Comentario", back_populates="tarea", cascade="all, delete-orphan", order_by="Comentario.fecha_creacion.desc()")


class Subtarea(Base):
    __tablename__ = "subtareas"

    id = Column(Integer, primary_key=True, index=True)
    tarea_id = Column(Integer, ForeignKey("tareas.id"), nullable=False)
    titulo = Column(String(200), nullable=False)
    completada = Column(Boolean, default=False)
    orden = Column(Integer, default=0)

    tarea = relationship("Tarea", back_populates="subtareas")


class Comentario(Base):
    __tablename__ = "comentarios"

    id = Column(Integer, primary_key=True, index=True)
    tarea_id = Column(Integer, ForeignKey("tareas.id"), nullable=False)
    autor = Column(String(80), default="Usuario")
    contenido = Column(Text, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    tarea = relationship("Tarea", back_populates="comentarios")
