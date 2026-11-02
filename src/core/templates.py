from pathlib import Path
from fastapi import Request
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "src" / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Filtros personalizados útiles para templates Jinja
def status_color(status: str) -> str:
    mapping = {
        "Listo": "#00c875",
        "En curso": "#fdab3d",
        "Bloqueado": "#e2445c",
        "En espera": "#579bfc",
        "Por iniciar": "#c4c4c4",
        "Backlog": "#784bd1"
    }
    return mapping.get(status, "#6c757d")

def priority_badge(priority: str) -> str:
    mapping = {
        "Crítica": "bg-danger",
        "Alta": "bg-warning text-dark",
        "Media": "bg-primary",
        "Baja": "bg-success"
    }
    return mapping.get(priority, "bg-secondary")

templates.env.filters["status_color"] = status_color
templates.env.filters["priority_badge"] = priority_badge


def render_template(request: Request, name: str, context: dict = None):
    ctx = context or {}
    return templates.TemplateResponse(request=request, name=name, context=ctx)
