from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from src.core.dependencies import get_db
from src.core.templates import render_template
from src.modules.tablero.service import TableroService
from src.modules.backlog.service import BacklogService
from src.modules.backlog.schema import SprintCreate, SprintUpdate, MoverSprint

router = APIRouter()


@router.get("/backlog", response_class=HTMLResponse)
def vista_backlog(
    request: Request,
    proyecto_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    user = request.session.get("user")
    proyectos = TableroService.get_proyectos(db, user)
    proyecto_actual = TableroService.get_proyecto_activo(db, proyecto_id, user)

    sprints = []
    tareas_sin_sprint = []
    sprint_activo = None

    if proyecto_actual:
        sprints = BacklogService.get_sprints_proyecto(db, proyecto_actual.id)
        tareas_sin_sprint = BacklogService.get_tareas_backlog_general(db, proyecto_actual.id)
        sprint_activo = next((s for s in sprints if s.estado == "Activo"), None)

    # Métricas de backlog
    total_puntos_backlog = sum(t.puntos_historia or 0 for t in tareas_sin_sprint)
    total_puntos_activo = sum(t.puntos_historia or 0 for t in sprint_activo.tareas) if sprint_activo else 0

    return render_template(
        request,
        "backlog/index.html",
        {
            "proyectos": proyectos,
            "proyecto_actual": proyecto_actual,
            "sprints": sprints,
            "sprint_activo": sprint_activo,
            "tareas_sin_sprint": tareas_sin_sprint,
            "total_puntos_backlog": total_puntos_backlog,
            "total_puntos_activo": total_puntos_activo,
            "modulo": "backlog",
        },
    )


@router.post("/api/sprints")
def crear_sprint(data: SprintCreate, db: Session = Depends(get_db)):
    nuevo = BacklogService.create_sprint(db, data)
    return {"ok": True, "id": nuevo.id, "nombre": nuevo.nombre, "estado": nuevo.estado}


@router.put("/api/sprints/{sprint_id}")
def actualizar_sprint(sprint_id: int, data: SprintUpdate, db: Session = Depends(get_db)):
    sprint = BacklogService.update_sprint(db, sprint_id, data)
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint no encontrado")
    return {"ok": True, "id": sprint.id, "nombre": sprint.nombre}


@router.patch("/api/sprints/{sprint_id}/estado")
def cambiar_estado(sprint_id: int, estado: str, db: Session = Depends(get_db)):
    sprint = BacklogService.cambiar_estado_sprint(db, sprint_id, estado)
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint no encontrado")
    return {"ok": True, "id": sprint.id, "estado": sprint.estado}


@router.patch("/api/tareas/{tarea_id}/mover-sprint")
def mover_tarea_sprint(tarea_id: int, data: MoverSprint, db: Session = Depends(get_db)):
    tarea = BacklogService.mover_tarea_sprint(db, tarea_id, data.sprint_id)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {"ok": True, "id": tarea.id, "sprint_id": tarea.sprint_id}
