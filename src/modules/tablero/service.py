from sqlalchemy.orm import Session
from src.models import Proyecto, Grupo, Tarea, Subtarea, Comentario, Sprint
from src.modules.tablero.schema import (
    TareaCreate,
    TareaUpdate,
    GrupoCreate,
    GrupoUpdate,
    ProyectoCreate,
    SubtareaCreate,
    ComentarioCreate,
)


class TableroService:
    @staticmethod
    def get_proyectos(db: Session, user_session: dict = None):
        if user_session and user_session.get("rol_alcance") == "uno" and user_session.get("proyecto_id"):
            return db.query(Proyecto).filter(Proyecto.id == user_session["proyecto_id"]).all()
        return db.query(Proyecto).all()

    @staticmethod
    def get_proyecto_activo(db: Session, proyecto_id: int = None, user_session: dict = None):
        if user_session and user_session.get("rol_alcance") == "uno" and user_session.get("proyecto_id"):
            return db.query(Proyecto).filter(Proyecto.id == user_session["proyecto_id"]).first()
        if proyecto_id:
            return db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
        return db.query(Proyecto).first()

    @staticmethod
    def create_proyecto(db: Session, data: ProyectoCreate):
        proyecto = Proyecto(
            nombre=data.nombre,
            clave=data.clave or "PRJ",
            descripcion=data.descripcion or "",
            color=data.color or "#6161FF",
        )
        db.add(proyecto)
        db.flush()

        # Crear grupos por defecto para el nuevo proyecto
        g1 = Grupo(proyecto_id=proyecto.id, titulo="📌 Tareas en progreso", color="#00C875", orden=1)
        g2 = Grupo(proyecto_id=proyecto.id, titulo="📋 Por hacer", color="#579BFC", orden=2)
        g3 = Grupo(proyecto_id=proyecto.id, titulo="📦 Backlog", color="#A25DDC", orden=3)
        db.add_all([g1, g2, g3])
        db.commit()
        db.refresh(proyecto)
        return proyecto

    @staticmethod
    def get_grupos_proyecto(db: Session, proyecto_id: int):
        return db.query(Grupo).filter(Grupo.proyecto_id == proyecto_id).order_by(Grupo.orden).all()

    @staticmethod
    def create_grupo(db: Session, data: GrupoCreate):
        max_orden = db.query(Grupo).filter(Grupo.proyecto_id == data.proyecto_id).count()
        grupo = Grupo(
            proyecto_id=data.proyecto_id,
            titulo=data.titulo,
            color=data.color or "#579BFC",
            orden=max_orden + 1,
        )
        db.add(grupo)
        db.commit()
        db.refresh(grupo)
        return grupo

    @staticmethod
    def update_grupo(db: Session, grupo_id: int, data: GrupoUpdate):
        grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
        if not grupo:
            return None
        if data.titulo is not None:
            grupo.titulo = data.titulo
        if data.color is not None:
            grupo.color = data.color
        if data.colapsado is not None:
            grupo.colapsado = data.colapsado
        db.commit()
        db.refresh(grupo)
        return grupo

    @staticmethod
    def delete_grupo(db: Session, grupo_id: int):
        grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
        if grupo:
            db.delete(grupo)
            db.commit()
            return True
        return False

    @staticmethod
    def create_tarea(db: Session, data: TareaCreate):
        max_orden = db.query(Tarea).filter(Tarea.grupo_id == data.grupo_id).count()
        tarea = Tarea(
            grupo_id=data.grupo_id,
            sprint_id=data.sprint_id,
            titulo=data.titulo,
            descripcion=data.descripcion or "",
            estado=data.estado or "Por iniciar",
            prioridad=data.prioridad or "Media",
            responsable=data.responsable or "Sin asignar",
            fecha_inicio=data.fecha_inicio,
            fecha_limite=data.fecha_limite,
            puntos_historia=data.puntos_historia if data.puntos_historia is not None else 1,
            tipo_tarea=data.tipo_tarea or "Tarea",
            orden=max_orden + 1,
        )
        db.add(tarea)
        db.commit()
        db.refresh(tarea)
        return tarea

    @staticmethod
    def update_tarea(db: Session, tarea_id: int, data: TareaUpdate):
        tarea = db.query(Tarea).filter(Tarea.id == tarea_id).first()
        if not tarea:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(tarea, field, value)
        db.commit()
        db.refresh(tarea)
        return tarea

    @staticmethod
    def update_tarea_estado(db: Session, tarea_id: int, estado: str):
        tarea = db.query(Tarea).filter(Tarea.id == tarea_id).first()
        if not tarea:
            return None
        tarea.estado = estado
        db.commit()
        db.refresh(tarea)
        return tarea

    @staticmethod
    def update_tarea_fecha(db: Session, tarea_id: int, fecha_limite, fecha_inicio=None):
        tarea = db.query(Tarea).filter(Tarea.id == tarea_id).first()
        if not tarea:
            return None
        tarea.fecha_limite = fecha_limite
        if fecha_inicio is not None:
            tarea.fecha_inicio = fecha_inicio
        db.commit()
        db.refresh(tarea)
        return tarea

    @staticmethod
    def mover_tarea(db: Session, tarea_id: int, nuevo_grupo_id: int, nuevo_orden: int = 0):
        tarea = db.query(Tarea).filter(Tarea.id == tarea_id).first()
        if not tarea:
            return None
        tarea.grupo_id = nuevo_grupo_id
        if nuevo_orden is not None:
            tarea.orden = nuevo_orden
        db.commit()
        db.refresh(tarea)
        return tarea

    @staticmethod
    def delete_tarea(db: Session, tarea_id: int):
        tarea = db.query(Tarea).filter(Tarea.id == tarea_id).first()
        if tarea:
            db.delete(tarea)
            db.commit()
            return True
        return False

    @staticmethod
    def get_tarea_detalle(db: Session, tarea_id: int):
        return db.query(Tarea).filter(Tarea.id == tarea_id).first()

    @staticmethod
    def add_subtarea(db: Session, tarea_id: int, data: SubtareaCreate):
        max_orden = db.query(Subtarea).filter(Subtarea.tarea_id == tarea_id).count()
        subtarea = Subtarea(
            tarea_id=tarea_id,
            titulo=data.titulo,
            completada=False,
            orden=max_orden + 1,
        )
        db.add(subtarea)
        db.commit()
        db.refresh(subtarea)
        return subtarea

    @staticmethod
    def toggle_subtarea(db: Session, subtarea_id: int):
        subtarea = db.query(Subtarea).filter(Subtarea.id == subtarea_id).first()
        if not subtarea:
            return None
        subtarea.completada = not subtarea.completada
        db.commit()
        db.refresh(subtarea)
        return subtarea

    @staticmethod
    def delete_subtarea(db: Session, subtarea_id: int):
        subtarea = db.query(Subtarea).filter(Subtarea.id == subtarea_id).first()
        if subtarea:
            db.delete(subtarea)
            db.commit()
            return True
        return False

    @staticmethod
    def add_comentario(db: Session, tarea_id: int, data: ComentarioCreate):
        comentario = Comentario(
            tarea_id=tarea_id,
            autor=data.autor or "Usuario",
            contenido=data.contenido,
        )
        db.add(comentario)
        db.commit()
        db.refresh(comentario)
        return comentario

