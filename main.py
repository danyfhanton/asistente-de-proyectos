"""
Asistente de Proyectos - Punto de entrada unificado estilo Monday / Jira accesible.

Un solo proceso, puerto 8000.
Conectado a Microsoft SQL Server local (localhost\\SQLEXPRESS) en la BD 'asistente_proyectos'.
Templates con Jinja2 y arquitectura modular.

    uvicorn main:app --port 8000 --reload
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from src.core.setup_db import ensure_local_sql_database
from src.core.seed import init_db
from src.core.session import SessionMiddleware

# Routers Modulares
from src.modules.auth.router import router as auth_router
from src.modules.usuarios.router import router as usuarios_router
from src.modules.roles.router import router as roles_router
from src.modules.tablero.router import router as tablero_router
from src.modules.backlog.router import router as backlog_router
from src.modules.dashboard.router import router as dashboard_router
from src.modules.actividades.router import router as actividades_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Garantizar base de datos y tablas en SQL Server local al iniciar
    ensure_local_sql_database()
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Sesiones de usuario
app.add_middleware(SessionMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos (CSS, JS, iconos)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Registro de Routers
app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(roles_router)
app.include_router(dashboard_router)
app.include_router(tablero_router)
app.include_router(backlog_router)
app.include_router(actividades_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
