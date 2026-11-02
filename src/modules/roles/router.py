import json
from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from src.core.dependencies import get_db
from src.core.templates import render_template
from src.modules.tablero.service import TableroService
from src.modules.roles.service import RolesService
from src.modules.roles.schema import RolCreate, RolUpdate

router = APIRouter()


@router.get("/roles", response_class=HTMLResponse)
def vista_roles(
    request: Request,
    proyecto_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    proyectos = TableroService.get_proyectos(db)
    proyecto_actual = TableroService.get_proyecto_activo(db, proyecto_id)
    roles = RolesService.get_roles(db)

    # Decodificar permisos para cada rol en la plantilla
    roles_data = []
    for r in roles:
        try:
            perms = json.loads(r.permisos) if r.permisos else []
        except Exception:
            perms = []
        roles_data.append({
            "id": r.id,
            "nombre": r.nombre,
            "descripcion": r.descripcion,
            "color": r.color,
            "alcance_proyectos": r.alcance_proyectos or "todos",
            "permisos": perms,
            "total_usuarios": len(r.usuarios),
            "fecha_creacion": r.fecha_creacion,
        })

    return render_template(
        request,
        "roles/index.html",
        {
            "proyectos": proyectos,
            "proyecto_actual": proyecto_actual,
            "roles": roles_data,
            "modulo": "roles",
        },
    )


@router.post("/api/roles")
def crear_rol(data: RolCreate, db: Session = Depends(get_db)):
    rol = RolesService.create_rol(db, data)
    return {"ok": True, "id": rol.id, "nombre": rol.nombre}


@router.put("/api/roles/{rol_id}")
def actualizar_rol(rol_id: int, data: RolUpdate, db: Session = Depends(get_db)):
    rol = RolesService.update_rol(db, rol_id, data)
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return {"ok": True, "id": rol.id, "nombre": rol.nombre}


@router.delete("/api/roles/{rol_id}")
def eliminar_rol(rol_id: int, db: Session = Depends(get_db)):
    ok = RolesService.delete_rol(db, rol_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return {"ok": True}

