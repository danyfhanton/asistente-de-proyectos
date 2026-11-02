from sqlalchemy.orm import Session
from src.models import Proyecto, Tarea, Sprint, Grupo


class DashboardService:
    @staticmethod
    def get_stats(db: Session, proyecto_id: int):
        proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
        if not proyecto:
            return {}

        tareas = (
            db.query(Tarea)
            .join(Tarea.grupo)
            .filter(Tarea.grupo.has(proyecto_id=proyecto_id))
            .all()
        )

        total = len(tareas)
        completadas = sum(1 for t in tareas if t.estado == "Listo")
        en_curso = sum(1 for t in tareas if t.estado == "En curso")
        en_espera = sum(1 for t in tareas if t.estado == "En espera")
        bloqueadas = sum(1 for t in tareas if t.estado == "Bloqueado")
        por_iniciar = sum(1 for t in tareas if t.estado == "Por iniciar")

        # Puntos de historia
        puntos_totales = sum(t.puntos_historia or 0 for t in tareas)
        puntos_completados = sum(t.puntos_historia or 0 for t in tareas if t.estado == "Listo")

        # Carga por responsable
        responsables = {}
        for t in tareas:
            resp = t.responsable or "Sin asignar"
            if resp not in responsables:
                responsables[resp] = {"total": 0, "completadas": 0, "puntos": 0}
            responsables[resp]["total"] += 1
            if t.estado == "Listo":
                responsables[resp]["completadas"] += 1
            responsables[resp]["puntos"] += (t.puntos_historia or 0)

        # Distribución por prioridad
        prioridades = {"Crítica": 0, "Alta": 0, "Media": 0, "Baja": 0}
        for t in tareas:
            if t.prioridad in prioridades:
                prioridades[t.prioridad] += 1

        # Sprints
        sprints = db.query(Sprint).filter(Sprint.proyecto_id == proyecto_id).all()

        return {
            "total": total,
            "completadas": completadas,
            "en_curso": en_curso,
            "en_espera": en_espera,
            "bloqueadas": bloqueadas,
            "por_iniciar": por_iniciar,
            "porcentaje_avance": int((completadas / total * 100)) if total > 0 else 0,
            "puntos_totales": puntos_totales,
            "puntos_completados": puntos_completados,
            "responsables": responsables,
            "prioridades": prioridades,
            "sprints_count": len(sprints),
        }

