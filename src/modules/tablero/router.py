from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session

from src.core.dependencies import get_db
from src.core.templates import render_template
from src.modules.tablero.service import TableroService
from src.modules.tablero.schema import (
    TareaCreate,
    TareaUpdate,
    TareaMover,
    FechaUpdate,
    EstadoUpdate,
    GrupoCreate,
    GrupoUpdate,
    ProyectoCreate,
    SubtareaCreate,
    ComentarioCreate,
)

router = APIRouter()


# ==========================================
# VISTAS HTML (JINJA2)
# ==========================================

@router.get("/tablero", response_class=HTMLResponse)
def vista_tablero(
    request: Request,
    proyecto_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    user = request.session.get("user")
    proyectos = TableroService.get_proyectos(db, user)
    proyecto_actual = TableroService.get_proyecto_activo(db, proyecto_id, user)
    grupos = []
    sprints = []

    if proyecto_actual:
        grupos = TableroService.get_grupos_proyecto(db, proyecto_actual.id)
        sprints = proyecto_actual.sprints

    # Resumen rápido del tablero
    total_tareas = sum(len(g.tareas) for g in grupos)
    completadas = sum(sum(1 for t in g.tareas if t.estado == "Listo") for g in grupos)
    en_curso = sum(sum(1 for t in g.tareas if t.estado == "En curso") for g in grupos)
    bloqueadas = sum(sum(1 for t in g.tareas if t.estado == "Bloqueado") for g in grupos)

    return render_template(
        request,
        "tablero/index.html",
        {
            "proyectos": proyectos,
            "proyecto_actual": proyecto_actual,
            "grupos": grupos,
            "sprints": sprints,
            "stats": {
                "total": total_tareas,
                "completadas": completadas,
                "en_curso": en_curso,
                "bloqueadas": bloqueadas,
                "progreso": int((completadas / total_tareas * 100)) if total_tareas > 0 else 0,
            },
            "modulo": "tablero",
        },
    )


@router.get("/tablero/kanban", response_class=HTMLResponse)
def vista_kanban(
    request: Request,
    proyecto_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    user = request.session.get("user")
    proyectos = TableroService.get_proyectos(db, user)
    proyecto_actual = TableroService.get_proyecto_activo(db, proyecto_id, user)

    columnas = {
        "Por iniciar": [],
        "En curso": [],
        "En espera": [],
        "Bloqueado": [],
        "Listo": [],
    }

    if proyecto_actual:
        for g in proyecto_actual.grupos:
            for t in g.tareas:
                if t.estado in columnas:
                    columnas[t.estado].append(t)
                else:
                    columnas["Por iniciar"].append(t)

    return render_template(
        request,
        "tablero/kanban.html",
        {
            "proyectos": proyectos,
            "proyecto_actual": proyecto_actual,
            "columnas": columnas,
            "modulo": "kanban",
        },
    )


# ==========================================
# ENDPOINTS API (JSON / ACCIONES AJAX)
# ==========================================

@router.post("/api/proyectos")
def crear_proyecto(data: ProyectoCreate, db: Session = Depends(get_db)):
    nuevo = TableroService.create_proyecto(db, data)
    return {"ok": True, "id": nuevo.id, "nombre": nuevo.nombre}


@router.post("/api/grupos")
def crear_grupo(data: GrupoCreate, db: Session = Depends(get_db)):
    nuevo = TableroService.create_grupo(db, data)
    return {"ok": True, "id": nuevo.id, "titulo": nuevo.titulo, "color": nuevo.color}


@router.put("/api/grupos/{grupo_id}")
def actualizar_grupo(grupo_id: int, data: GrupoUpdate, db: Session = Depends(get_db)):
    grupo = TableroService.update_grupo(db, grupo_id, data)
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return {"ok": True, "id": grupo.id, "titulo": grupo.titulo}


@router.delete("/api/grupos/{grupo_id}")
def eliminar_grupo(grupo_id: int, db: Session = Depends(get_db)):
    ok = TableroService.delete_grupo(db, grupo_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return {"ok": True}


@router.post("/api/tareas")
def crear_tarea(data: TareaCreate, db: Session = Depends(get_db)):
    tarea = TableroService.create_tarea(db, data)
    return {
        "ok": True,
        "id": tarea.id,
        "titulo": tarea.titulo,
        "estado": tarea.estado,
        "prioridad": tarea.prioridad,
        "responsable": tarea.responsable,
        "puntos_historia": tarea.puntos_historia,
    }


@router.put("/api/tareas/{tarea_id}")
def actualizar_tarea(tarea_id: int, data: TareaUpdate, db: Session = Depends(get_db)):
    tarea = TableroService.update_tarea(db, tarea_id, data)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {"ok": True, "id": tarea.id, "titulo": tarea.titulo, "estado": tarea.estado}


@router.patch("/api/tareas/{tarea_id}/estado")
def actualizar_estado_tarea(tarea_id: int, data: EstadoUpdate, db: Session = Depends(get_db)):
    tarea = TableroService.update_tarea_estado(db, tarea_id, data.estado)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {"ok": True, "id": tarea.id, "estado": tarea.estado}


@router.patch("/api/tareas/{tarea_id}/fecha")
def actualizar_fecha_tarea(tarea_id: int, data: FechaUpdate, db: Session = Depends(get_db)):
    tarea = TableroService.update_tarea_fecha(db, tarea_id, data.fecha_limite, data.fecha_inicio)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {
        "ok": True,
        "id": tarea.id,
        "fecha_limite": tarea.fecha_limite.isoformat() if tarea.fecha_limite else None,
        "fecha_inicio": tarea.fecha_inicio.isoformat() if tarea.fecha_inicio else None,
    }


@router.patch("/api/tareas/{tarea_id}/mover")
def mover_tarea(tarea_id: int, data: TareaMover, db: Session = Depends(get_db)):
    tarea = TableroService.mover_tarea(db, tarea_id, data.grupo_id, data.nuevo_orden)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {"ok": True, "id": tarea.id, "grupo_id": tarea.grupo_id, "orden": tarea.orden}


@router.delete("/api/tareas/{tarea_id}")
def eliminar_tarea(tarea_id: int, db: Session = Depends(get_db)):
    ok = TableroService.delete_tarea(db, tarea_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {"ok": True}


@router.get("/api/tareas/{tarea_id}/detalle")
def obtener_detalle_tarea(tarea_id: int, db: Session = Depends(get_db)):
    tarea = TableroService.get_tarea_detalle(db, tarea_id)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    return {
        "id": tarea.id,
        "titulo": tarea.titulo,
        "descripcion": tarea.descripcion,
        "estado": tarea.estado,
        "prioridad": tarea.prioridad,
        "responsable": tarea.responsable,
        "fecha_inicio": tarea.fecha_inicio.isoformat() if tarea.fecha_inicio else None,
        "fecha_limite": tarea.fecha_limite.isoformat() if tarea.fecha_limite else None,
        "puntos_historia": tarea.puntos_historia,
        "tipo_tarea": tarea.tipo_tarea,
        "grupo_id": tarea.grupo_id,
        "sprint_id": tarea.sprint_id,
        "subtareas": [
            {"id": s.id, "titulo": s.titulo, "completada": s.completada}
            for s in tarea.subtareas
        ],
        "comentarios": [
            {
                "id": c.id,
                "autor": c.autor,
                "contenido": c.contenido,
                "fecha": c.fecha_creacion.strftime("%d/%m/%Y %H:%M"),
            }
            for c in tarea.comentarios
        ],
    }


@router.post("/api/tareas/{tarea_id}/subtareas")
def agregar_subtarea(tarea_id: int, data: SubtareaCreate, db: Session = Depends(get_db)):
    sub = TableroService.add_subtarea(db, tarea_id, data)
    return {"ok": True, "id": sub.id, "titulo": sub.titulo, "completada": sub.completada}


@router.patch("/api/subtareas/{subtarea_id}/toggle")
def toggle_subtarea(subtarea_id: int, db: Session = Depends(get_db)):
    sub = TableroService.toggle_subtarea(db, subtarea_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subtarea no encontrada")
    return {"ok": True, "id": sub.id, "completada": sub.completada}


@router.delete("/api/subtareas/{subtarea_id}")
def eliminar_subtarea(subtarea_id: int, db: Session = Depends(get_db)):
    ok = TableroService.delete_subtarea(db, subtarea_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Subtarea no encontrada")
    return {"ok": True}


@router.post("/api/tareas/{tarea_id}/comentarios")
def agregar_comentario(tarea_id: int, data: ComentarioCreate, db: Session = Depends(get_db)):
    c = TableroService.add_comentario(db, tarea_id, data)
    return {
        "ok": True,
        "id": c.id,
        "autor": c.autor,
        "contenido": c.contenido,
        "fecha": c.fecha_creacion.strftime("%d/%m/%Y %H:%M"),
    }
