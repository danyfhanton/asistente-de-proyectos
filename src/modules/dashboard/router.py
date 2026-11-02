from typing import Optional
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.core.dependencies import get_db
from src.core.templates import render_template
from src.modules.tablero.service import TableroService
from src.modules.dashboard.service import DashboardService

router = APIRouter()


@router.get("/", response_class=RedirectResponse)
def root_redirect():
    return RedirectResponse(url="/tablero")


@router.get("/dashboard", response_class=HTMLResponse)
def vista_dashboard(
    request: Request,
    proyecto_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    user = request.session.get("user")
    proyectos = TableroService.get_proyectos(db, user)
    proyecto_actual = TableroService.get_proyecto_activo(db, proyecto_id, user)

    stats = {}
    if proyecto_actual:
        stats = DashboardService.get_stats(db, proyecto_actual.id)

    return render_template(
        request,
        "dashboard/index.html",
        {
            "proyectos": proyectos,
            "proyecto_actual": proyecto_actual,
            "stats": stats,
            "modulo": "dashboard",
        },
    )


@router.get("/api/dashboard/stats")
def api_dashboard_stats(
    proyecto_id: int,
    db: Session = Depends(get_db),
):
    return DashboardService.get_stats(db, proyecto_id)
