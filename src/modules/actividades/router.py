import csv
import io
import json
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Request, Response, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session

from src.core.dependencies import get_db
from src.core.templates import render_template
from src.models import Comentario, Tarea, Proyecto, Grupo, Subtarea
from src.modules.tablero.service import TableroService

router = APIRouter()


@router.get("/actividades", response_class=HTMLResponse)
def vista_actividades(
    request: Request,
    proyecto_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    user = request.session.get("user")
    proyectos = TableroService.get_proyectos(db, user)
    proyecto_actual = TableroService.get_proyecto_activo(db, proyecto_id, user)

    comentarios = []
    tareas_recientes = []
    if proyecto_actual:
        comentarios = (
            db.query(Comentario)
            .join(Comentario.tarea)
            .join(Tarea.grupo)
            .filter(Tarea.grupo.has(proyecto_id=proyecto_actual.id))
            .order_by(Comentario.fecha_creacion.desc())
            .limit(30)
            .all()
        )
        tareas_recientes = (
            db.query(Tarea)
            .join(Tarea.grupo)
            .filter(Tarea.grupo.has(proyecto_id=proyecto_actual.id))
            .order_by(Tarea.fecha_actualizacion.desc())
            .limit(20)
            .all()
        )

    return render_template(
        request,
        "actividades/index.html",
        {
            "proyectos": proyectos,
            "proyecto_actual": proyecto_actual,
            "comentarios": comentarios,
            "tareas_recientes": tareas_recientes,
            "modulo": "actividades",
        },
    )


@router.get("/exportar/csv")
def exportar_csv(
    proyecto_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    proyecto = TableroService.get_proyecto_activo(db, proyecto_id)
    if not proyecto:
        return Response(content="Proyecto no encontrado", status_code=404)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Grupo", "Título", "Estado", "Prioridad", "Responsable",
        "Puntos Historia", "Tipo", "Fecha Inicio", "Fecha Límite"
    ])

    for grupo in proyecto.grupos:
        for t in grupo.tareas:
            writer.writerow([
                t.id,
                grupo.titulo,
                t.titulo,
                t.estado,
                t.prioridad,
                t.responsable,
                t.puntos_historia,
                t.tipo_tarea,
                t.fecha_inicio.strftime("%Y-%m-%d") if t.fecha_inicio else "",
                t.fecha_limite.strftime("%Y-%m-%d") if t.fecha_limite else "",
            ])

    output.seek(0)
    filename = f"export_{proyecto.clave}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/exportar/json")
def exportar_json(
    proyecto_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    proyecto = TableroService.get_proyecto_activo(db, proyecto_id)
    if not proyecto:
        return Response(content="Proyecto no encontrado", status_code=404)

    data = {
        "proyecto": {
            "nombre": proyecto.nombre,
            "clave": proyecto.clave,
            "descripcion": proyecto.descripcion,
            "color": proyecto.color,
        },
        "grupos": [],
    }

    for g in proyecto.grupos:
        grupo_data = {
            "titulo": g.titulo,
            "color": g.color,
            "tareas": [],
        }
        for t in g.tareas:
            grupo_data["tareas"].append({
                "titulo": t.titulo,
                "descripcion": t.descripcion,
                "estado": t.estado,
                "prioridad": t.prioridad,
                "responsable": t.responsable,
                "puntos_historia": t.puntos_historia,
                "tipo_tarea": t.tipo_tarea,
                "subtareas": [{"titulo": s.titulo, "completada": s.completada} for s in t.subtareas],
            })
        data["grupos"].append(grupo_data)

    content = json.dumps(data, ensure_ascii=False, indent=2)
    filename = f"backup_{proyecto.clave}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
