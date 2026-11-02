# Asistente de Proyectos (Estilo Monday / Jira Accesible)

Aplicación web para gestión de proyectos, actividades ágiles y backlogs basada en las mejores prácticas de la arquitectura modular de `data-intelligence-medicasur-recepcion-app`, construida con **Python**, **FastAPI**, **Jinja2** y conectada a la base de datos **Microsoft SQL Server Local (`localhost\SQLEXPRESS`)**.

---

## 🚀 Características Principales

1. **Tablero Interactivo estilo Monday.com (`/tablero`)**:
   - **Renombrado interactivo de grupos:** Clic en el nombre del grupo o en el icono de edición para renombrarlo al instante con guardado en SQL Server.
   - **Visualización de Sub-elementos en el Tablero:** Botón desplegable (`>` / `v`) e indicador de progreso en cada actividad para ver, marcar como completados, agregar o eliminar sub-elementos directamente en la tabla sin abrir modales.
   - **Columnas con estados en bloques de colores Monday:** *Listo*, *En curso*, *En espera*, *Bloqueado*, *Por iniciar* con cambio rápido al hacer clic.
   - **Selector interactivo de prioridades:** *Crítica*, *Alta*, *Media*, *Baja*.
   - **Gestión de Fechas Dinámicas:** Campo de fecha integrado al crear actividades y selector inline en cada fila sincronizado por AJAX (`PATCH /api/tareas/{id}/fecha`).
   - **Reordenamiento dinámico de filas (Drag & Drop):** Arrastra y suelta filas entre o dentro de grupos con persistencia en SQL Server (`PATCH /api/tareas/{id}/mover`).

2. **Tablero Kanban con Drag & Drop (`/tablero/kanban`)**:
   - Columnas organizadas por estado.
   - Arrastre interactivo de tarjetas que actualiza el estado en SQL Server en tiempo real mediante AJAX.
   - Indicadores de puntos de historia y avance de subtareas por tarjeta.

3. **Gestión de Backlog & Sprints (`/backlog`)**:
   - Planificación de Sprints (Crear sprint, Iniciar Sprint, Completar Sprint).
   - Asignación de tareas entre el Backlog General y Sprints activos.
   - Cálculo automático de velocidad y puntos de historia.

5. **Administración de Roles & Permisos (`/roles`)**:
   - **Control de Alcance de Proyectos:** Puedes elegir para cada rol si sus usuarios tienen visibilidad de **Todos los proyectos** (acceso global) o **Solo un proyecto** (restringido al proyecto que tienen asignado).
   - Tarjetas de roles con distintivo de color, descripción, contador de usuarios vinculados, insignia de alcance y etiquetas de permisos.
   - Creación y edición dinámica de roles con persistencia en SQL Server.

6. **Administración de Usuarios (`/usuarios`)**:
   - Directorio de colaboradores con asignación de rol y **Proyecto Asignado**.
   - Si el rol asignado está configurado para *Solo 1 proyecto*, el sistema restringe automáticamente su navegación y dropdown exclusivamente a su proyecto designado.
   - Switch interactivo para activar o suspender usuarios de inmediato.
   - Creación y edición con modal emergente y contraseñas cifradas en **SHA-256**.

6. **Pantalla de Inicio de Sesión Corporativa (`/login`)**:
   - Diseño split-screen dual inspirado en los portales corporativos.
   - Panel izquierdo con formulario de ingreso (email y contraseña con visualizador toggle).
   - Panel derecho con información del portal, resumen de capacidades y características de la plataforma.

7. **Dashboard & Métricas Analíticas (`/dashboard`)**:
   - KPIs de avance global, velocidad del equipo y bloqueos.
   - Gráfico de dona con distribución de estados y gráfico de barras con carga de trabajo por integrante (Chart.js).

8. **Auditoría, Comentarios y Exportación (`/actividades`)**:
   - Feed de actualizaciones y comentarios en tiempo real por actividad.
   - Exportación de actividades a archivo **CSV** compatible con Excel y respaldo integral en formato **JSON**.

---

## 🔑 Credenciales Demo Preconfiguradas en SQL Server

| Nombre | Correo Electrónico | Contraseña | Rol Asignado |
| :--- | :--- | :--- | :--- |
| **Daniel Fhanton** | `admin@proyectos.local` | `admin123` | **Administrador** |
| **Sofia López** | `sofia.lopez@proyectos.local` | `sofia123` | **Scrum Master** |
| **Carlos Mendoza** | `carlos.mendoza@proyectos.local` | `carlos123` | **Desarrollador** |

---

## 🗄️ Base de Datos SQL Server Local

La aplicación apunta directamente a tu instancia local de SQL Server:
- **Servidor:** `localhost\SQLEXPRESS`
- **Base de datos:** `asistente_proyectos`
- **Driver:** `ODBC Driver 18 for SQL Server`
- **Autenticación:** Integrada de Windows (`Trusted_Connection=yes`)

---

## ▶️ Cómo Iniciar la Aplicación

1. **Activar el entorno virtual e iniciar el servidor con Uvicorn**:
   ```powershell
   .\venv\Scripts\uvicorn.exe main:app --port 8000 --reload
   ```

2. **Abrir en el navegador**:
   ```
   http://127.0.0.1:8000/tablero
   ```
