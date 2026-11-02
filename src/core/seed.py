import json
from datetime import date, datetime, timedelta
from src.core.database import SessionLocal, Base, engine
from src.core.security import hash_password
from src.models import Rol, Usuario, Proyecto, Sprint, Grupo, Tarea, Subtarea, Comentario


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 1. Sembrar Roles si no existen
        if db.query(Rol).first() is None:
            r_admin = Rol(
                nombre="Administrador",
                descripcion="Acceso total al sistema, gestión de usuarios, roles, proyectos y configuración",
                color="#E2445C",
                alcance_proyectos="todos",
                permisos=json.dumps(["admin", "proyectos", "tareas", "sprints", "usuarios", "roles", "exportar"]),
            )
            r_scrum = Rol(
                nombre="Scrum Master",
                descripcion="Facilitador ágil, gestión de sprints, tableros y métricas de velocidad",
                color="#6161FF",
                alcance_proyectos="todos",
                permisos=json.dumps(["proyectos", "tareas", "sprints", "metricas", "tablero"]),
            )
            r_po = Rol(
                nombre="Product Owner",
                descripcion="Definición y priorización del backlog, historias de usuario y visión del producto",
                color="#FDAB3D",
                alcance_proyectos="todos",
                permisos=json.dumps(["proyectos", "tareas", "backlog", "metricas"]),
            )
            r_dev = Rol(
                nombre="Desarrollador",
                descripcion="Ejecución de tareas, checklist de subtareas y feed de comentarios",
                color="#00C875",
                alcance_proyectos="uno",
                permisos=json.dumps(["tareas_editar", "subtareas", "comentarios", "tablero"]),
            )
            r_viewer = Rol(
                nombre="Visualizador",
                descripcion="Acceso de solo lectura a los tableros, backlog y métricas del proyecto",
                color="#579BFC",
                alcance_proyectos="uno",
                permisos=json.dumps(["lectura"]),
            )
            db.add_all([r_admin, r_scrum, r_po, r_dev, r_viewer])
            db.flush()

            # 2. Sembrar Usuarios iniciales
            u1 = Usuario(
                nombre="Daniel Fhanton",
                email="admin@proyectos.local",
                password_hash=hash_password("admin123"),
                rol_id=r_admin.id,
                cargo="Lead Architect & Project Manager",
                activo=True,
                avatar_color="#6161FF",
            )
            u2 = Usuario(
                nombre="Sofia López",
                email="sofia.lopez@proyectos.local",
                password_hash=hash_password("sofia123"),
                rol_id=r_scrum.id,
                cargo="Scrum Master",
                activo=True,
                avatar_color="#FDAB3D",
            )
            u3 = Usuario(
                nombre="Carlos Mendoza",
                email="carlos.mendoza@proyectos.local",
                password_hash=hash_password("carlos123"),
                rol_id=r_dev.id,
                cargo="Full Stack Developer",
                activo=True,
                avatar_color="#00C875",
            )
            db.add_all([u1, u2, u3])
            db.flush()

        # 3. Sembrar Proyecto Demo si no existe
        if db.query(Proyecto).first() is None:
            proyecto = Proyecto(
                nombre="Lanzamiento Asistente de Proyectos",
                clave="AST",
                descripcion="Tablero de control de actividades, desarrollo de features y backlog del proyecto",
                color="#6161FF",
            )
            db.add(proyecto)
            db.flush()

            hoy = date.today()
            sprint_1 = Sprint(
                proyecto_id=proyecto.id,
                nombre="Sprint 1 - MVP & Base Core",
                objetivo="Configurar la estructura base, vista de tabla interactiva y tablero kanban estilo Monday",
                estado="Activo",
                fecha_inicio=hoy - timedelta(days=3),
                fecha_fin=hoy + timedelta(days=11),
            )
            sprint_2 = Sprint(
                proyecto_id=proyecto.id,
                nombre="Sprint 2 - Automatizaciones & Métricas",
                objetivo="Gráficos de burndown, exportación a Excel y notificaciones de actividad",
                estado="Planificado",
                fecha_inicio=hoy + timedelta(days=12),
                fecha_fin=hoy + timedelta(days=26),
            )
            db.add_all([sprint_1, sprint_2])
            db.flush()

            # Grupos estilo Monday
            g_sprint = Grupo(
                proyecto_id=proyecto.id,
                titulo="🚀 En progreso en el Sprint actual",
                color="#00C875",
                orden=1,
            )
            g_proximas = Grupo(
                proyecto_id=proyecto.id,
                titulo="📋 Próximas actividades prioritarias",
                color="#579BFC",
                orden=2,
            )
            g_backlog = Grupo(
                proyecto_id=proyecto.id,
                titulo="📦 Backlog general de ideas y mejoras",
                color="#A25DDC",
                orden=3,
            )
            db.add_all([g_sprint, g_proximas, g_backlog])
            db.flush()

            # Tareas del Sprint
            t1 = Tarea(
                grupo_id=g_sprint.id,
                sprint_id=sprint_1.id,
                titulo="Diseñar la interfaz de tablero estilo Monday.com",
                descripcion="Implementar columnas interactivas, estados con colores visuales y cabecera de grupo",
                estado="Listo",
                prioridad="Alta",
                responsable="Daniel F.",
                fecha_inicio=hoy - timedelta(days=2),
                fecha_limite=hoy,
                puntos_historia=5,
                tipo_tarea="Historia",
                orden=1,
            )
            t2 = Tarea(
                grupo_id=g_sprint.id,
                sprint_id=sprint_1.id,
                titulo="Construir vista Kanban con Drag & Drop dinámico",
                descripcion="Permitir arrastrar tarjetas entre Por iniciar, En curso, En espera, Bloqueado y Listo",
                estado="En curso",
                prioridad="Crítica",
                responsable="Sofia L.",
                fecha_inicio=hoy - timedelta(days=1),
                fecha_limite=hoy + timedelta(days=3),
                puntos_historia=8,
                tipo_tarea="Historia",
                orden=2,
            )
            t3 = Tarea(
                grupo_id=g_sprint.id,
                sprint_id=sprint_1.id,
                titulo="API modular en FastAPI con Jinja2 y SQL Server",
                descripcion="Seguir las mejores prácticas corporativas del ecosistema Python modular",
                estado="Listo",
                prioridad="Alta",
                responsable="Daniel F.",
                fecha_inicio=hoy - timedelta(days=3),
                fecha_limite=hoy,
                puntos_historia=5,
                tipo_tarea="Tarea",
                orden=3,
            )

            # Tareas de Próximas actividades
            t4 = Tarea(
                grupo_id=g_proximas.id,
                sprint_id=sprint_1.id,
                titulo="Filtro rápido por responsable, estado y prioridad",
                descripcion="Barra de herramientas estilo Monday con búsqueda instantánea y filtros combinados",
                estado="Por iniciar",
                prioridad="Media",
                responsable="Sofia L.",
                fecha_inicio=hoy + timedelta(days=1),
                fecha_limite=hoy + timedelta(days=5),
                puntos_historia=3,
                tipo_tarea="Mejora",
                orden=1,
            )
            t5 = Tarea(
                grupo_id=g_proximas.id,
                sprint_id=sprint_1.id,
                titulo="Modal de detalle de actividad con sub-tareas y comentarios",
                descripcion="Checklist interactivo y feed de actualizaciones para cada tarea",
                estado="En espera",
                prioridad="Media",
                responsable="Carlos M.",
                fecha_inicio=hoy + timedelta(days=2),
                fecha_limite=hoy + timedelta(days=6),
                puntos_historia=5,
                tipo_tarea="Historia",
                orden=2,
            )

            # Tareas en Backlog
            t6 = Tarea(
                grupo_id=g_backlog.id,
                sprint_id=sprint_2.id,
                titulo="Dashboard con métricas de avance y Burndown Chart",
                descripcion="Cálculo automático de velocidad de sprint, distribución de estados y progreso",
                estado="Por iniciar",
                prioridad="Alta",
                responsable="Daniel F.",
                fecha_inicio=hoy + timedelta(days=12),
                fecha_limite=hoy + timedelta(days=20),
                puntos_historia=8,
                tipo_tarea="Historia",
                orden=1,
            )
            t7 = Tarea(
                grupo_id=g_backlog.id,
                sprint_id=None,
                titulo="Exportar actividades a formato Excel / CSV / JSON",
                descripcion="Botón de exportación rápida para reportes gerenciales",
                estado="Por iniciar",
                prioridad="Baja",
                responsable="Carlos M.",
                puntos_historia=2,
                tipo_tarea="Mejora",
                orden=2,
            )
            db.add_all([t1, t2, t3, t4, t5, t6, t7])
            db.flush()

            # Subtareas de ejemplo
            st1 = Subtarea(tarea_id=t1.id, titulo="Definir paleta de colores Monday", completada=True, orden=1)
            st2 = Subtarea(tarea_id=t1.id, titulo="Crear estructura Jinja con base.html", completada=True, orden=2)
            st3 = Subtarea(tarea_id=t2.id, titulo="Integrar eventos dragstart y dragover", completada=True, orden=1)
            st4 = Subtarea(tarea_id=t2.id, titulo="Endpoint PATCH para cambio de estado", completada=False, orden=2)
            db.add_all([st1, st2, st3, st4])

            # Comentario de ejemplo
            c1 = Comentario(
                tarea_id=t2.id,
                autor="Daniel F.",
                contenido="Se implementó la sincronización instantánea vía AJAX sin recargar la página.",
            )
            db.add(c1)

        db.commit()
    finally:
        db.close()
