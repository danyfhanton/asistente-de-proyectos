from typing import Optional
from fastapi import APIRouter, Depends, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

from src.core.dependencies import get_db
from src.core.templates import render_template
from src.modules.auth.service import AuthService

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
def vista_login(request: Request, msg: Optional[str] = None, error: Optional[bool] = False):
    user = request.session.get("user")
    if user:
        return RedirectResponse(url="/tablero")

    return render_template(
        request,
        "auth/login.html",
        {
            "msg": msg,
            "error": error,
        },
    )


@router.post("/auth/login")
async def process_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    result = AuthService.authenticate(db, email, password)
    if result == "inactivo":
        return render_template(
            request,
            "auth/login.html",
            {
                "msg": "Tu cuenta de usuario se encuentra inactiva. Contacta al administrador.",
                "error": True,
            },
        )
    elif result is None:
        return render_template(
            request,
            "auth/login.html",
            {
                "msg": "Credenciales inválidas. Por favor verifica tu correo o contraseña.",
                "error": True,
            },
        )

    # Autenticación exitosa -> Guardar en sesión
    user = result
    request.session["user"] = {
        "id": user.id,
        "nombre": user.nombre,
        "email": user.email,
        "rol": user.rol.nombre if user.rol else "Colaborador",
        "rol_color": user.rol.color if user.rol else "#6161FF",
        "rol_alcance": user.rol.alcance_proyectos if user.rol else "todos",
        "proyecto_id": user.proyecto_id,
        "cargo": user.cargo,
        "avatar_color": user.avatar_color,
    }

    return RedirectResponse(url="/tablero", status_code=303)


@router.get("/auth/logout")
def process_logout(request: Request):
    if "user" in request.session:
        del request.session["user"]
    return RedirectResponse(url="/login")


@router.get("/api/auth/me")
def api_current_user(request: Request):
    user = request.session.get("user")
    return {"authenticated": user is not None, "user": user}

