from sqlalchemy.orm import Session
from src.models import Sprint, Tarea, Proyecto
from src.modules.backlog.schema import SprintCreate, SprintUpdate


class BacklogService:
    @staticmethod
    def get_sprints_proyecto(db: Session, proyecto_id: int):
        return db.query(Sprint).filter(Sprint.proyecto_id == proyecto_id).order_by(Sprint.id.desc()).all()

    @staticmethod
    def get_tareas_backlog_general(db: Session, proyecto_id: int):
        # Tareas del proyecto que no están asignadas a ningún sprint
        return (
            db.query(Tarea)
            .join(Tarea.grupo)
            .filter(Tarea.grupo.has(proyecto_id=proyecto_id), Tarea.sprint_id == None)
            .order_by(Tarea.orden)
            .all()
        )

    @staticmethod
    def create_sprint(db: Session, data: SprintCreate):
        sprint = Sprint(
            proyecto_id=data.proyecto_id,
            nombre=data.nombre,
            objetivo=data.objetivo or "",
            estado="Planificado",
            fecha_inicio=data.fecha_inicio,
            fecha_fin=data.fecha_fin,
        )
        db.add(sprint)
        db.commit()
        db.refresh(sprint)
        return sprint

    @staticmethod
    def update_sprint(db: Session, sprint_id: int, data: SprintUpdate):
        sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
        if not sprint:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(sprint, field, value)
        db.commit()
        db.refresh(sprint)
        return sprint

    @staticmethod
    def cambiar_estado_sprint(db: Session, sprint_id: int, nuevo_estado: str):
        sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
        if not sprint:
            return None
        sprint.estado = nuevo_estado
        db.commit()
        db.refresh(sprint)
        return sprint

    @staticmethod
    def mover_tarea_sprint(db: Session, tarea_id: int, sprint_id: int = None):
        tarea = db.query(Tarea).filter(Tarea.id == tarea_id).first()
        if not tarea:
            return None
        tarea.sprint_id = sprint_id
        db.commit()
        db.refresh(tarea)
        return tarea

