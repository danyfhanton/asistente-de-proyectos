from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from src.core.dependencies import get_db
from src.core.templates import render_template
from src.modules.tablero.service import TableroService
from src.modules.roles.service import RolesService
from src.modules.usuarios.service import UsuariosService
from src.modules.usuarios.schema import UsuarioCreate, UsuarioUpdate

router = APIRouter()


@router.get("/usuarios", response_class=HTMLResponse)
def vista_usuarios(
    request: Request,
    proyecto_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    user = request.session.get("user")
    proyectos = TableroService.get_proyectos(db, user)
    todos_los_proyectos = TableroService.get_proyectos(db)
    proyecto_actual = TableroService.get_proyecto_activo(db, proyecto_id, user)
    usuarios = UsuariosService.get_usuarios(db)
    roles = RolesService.get_roles(db)

    return render_template(
        request,
        "usuarios/index.html",
        {
            "proyectos": proyectos,
            "todos_los_proyectos": todos_los_proyectos,
            "proyecto_actual": proyecto_actual,
            "usuarios": usuarios,
            "roles": roles,
            "modulo": "usuarios",
        },
    )


@router.post("/api/usuarios")
def crear_usuario(data: UsuarioCreate, db: Session = Depends(get_db)):
    nuevo = UsuariosService.create_usuario(db, data)
    if not nuevo:
        raise HTTPException(status_code=400, detail="El correo electrónico ya se encuentra registrado")
    return {"ok": True, "id": nuevo.id, "nombre": nuevo.nombre}


@router.put("/api/usuarios/{user_id}")
def actualizar_usuario(user_id: int, data: UsuarioUpdate, db: Session = Depends(get_db)):
    user = UsuariosService.update_usuario(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"ok": True, "id": user.id, "nombre": user.nombre}


@router.patch("/api/usuarios/{user_id}/toggle-activo")
def toggle_activo(user_id: int, db: Session = Depends(get_db)):
    user = UsuariosService.toggle_activo(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"ok": True, "id": user.id, "activo": user.activo}


@router.delete("/api/usuarios/{user_id}")
def eliminar_usuario(user_id: int, db: Session = Depends(get_db)):
    ok = UsuariosService.delete_usuario(db, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"ok": True}

