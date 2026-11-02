// Asistente de Proyectos - Interacciones Frontend estilo Monday.com

const Toast = Swal.mixin({
  toast: true,
  position: 'top-end',
  showConfirmButton: false,
  timer: 2500,
  timerProgressBar: true,
});

// ==========================================
// ACCIONES DE TABLERO MONDAY
// ==========================================

// Cambiar estado inline
async function cambiarEstado(tareaId, nuevoEstado) {
  try {
    const res = await fetch(`/api/tareas/${tareaId}/estado`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ estado: nuevoEstado }),
    });
    if (res.ok) {
      Toast.fire({ icon: 'success', title: `Estado: ${nuevoEstado}` });
      setTimeout(() => location.reload(), 400);
    } else {
      Toast.fire({ icon: 'error', title: 'Error al cambiar estado' });
    }
  } catch (e) {
    console.error(e);
    Toast.fire({ icon: 'error', title: 'Error de red' });
  }
}

// Selector emergente de estado
function abrirSelectorEstado(event, tareaId) {
  event.stopPropagation();
  const estados = [
    { nombre: 'Listo', color: '#00C875' },
    { nombre: 'En curso', color: '#FDAB3D' },
    { nombre: 'En espera', color: '#579BFC' },
    { nombre: 'Bloqueado', color: '#E2445C' },
    { nombre: 'Por iniciar', color: '#C4C4C4' },
  ];

  let html = '<div style="display:flex; flex-direction:column; gap:8px;">';
  estados.forEach(e => {
    html += `<button class="btn text-white w-100 fw-bold" style="background:${e.color};" onclick="Swal.close(); cambiarEstado(${tareaId}, '${e.nombre}')">${e.nombre}</button>`;
  });
  html += '</div>';

  Swal.fire({
    title: 'Cambiar Estado',
    html: html,
    showConfirmButton: false,
    showCloseButton: true,
    width: 320,
  });
}

// Selector emergente de prioridad
function abrirSelectorPrioridad(event, tareaId) {
  event.stopPropagation();
  const prioridades = [
    { nombre: 'Crítica', color: '#784BD1' },
    { nombre: 'Alta', color: '#E2445C' },
    { nombre: 'Media', color: '#579BFC' },
    { nombre: 'Baja', color: '#00C875' },
  ];

  let html = '<div style="display:flex; flex-direction:column; gap:8px;">';
  prioridades.forEach(p => {
    html += `<button class="btn text-white w-100 fw-bold" style="background:${p.color};" onclick="Swal.close(); actualizarCampoTarea(${tareaId}, {prioridad: '${p.nombre}'})">${p.nombre}</button>`;
  });
  html += '</div>';

  Swal.fire({
    title: 'Cambiar Prioridad',
    html: html,
    showConfirmButton: false,
    showCloseButton: true,
    width: 320,
  });
}

// Actualizar cualquier campo de una tarea
async function actualizarCampoTarea(tareaId, campos) {
  try {
    const res = await fetch(`/api/tareas/${tareaId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(campos),
    });
    if (res.ok) {
      Toast.fire({ icon: 'success', title: 'Tarea actualizada' });
      setTimeout(() => location.reload(), 350);
    }
  } catch (e) {
    console.error(e);
    Toast.fire({ icon: 'error', title: 'Error al actualizar' });
  }
}

// Actualizar fecha directamente inline estilo Monday
async function actualizarFechaTarea(tareaId, nuevaFecha) {
  try {
    const res = await fetch(`/api/tareas/${tareaId}/fecha`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fecha_limite: nuevaFecha ? nuevaFecha : null }),
    });
    if (res.ok) {
      Toast.fire({ icon: 'success', title: 'Fecha límite actualizada' });
    } else {
      Toast.fire({ icon: 'error', title: 'No se pudo actualizar la fecha' });
    }
  } catch (e) {
    console.error(e);
    Toast.fire({ icon: 'error', title: 'Error de conexión' });
  }
}

// Crear actividad con fecha opcional inline estilo Monday
async function crearTareaConFecha(grupoId) {
  const inputTitulo = document.getElementById(`input-task-${grupoId}`);
  const inputFecha = document.getElementById(`date-task-${grupoId}`);

  const titulo = inputTitulo.value.trim();
  const fecha = inputFecha ? inputFecha.value : null;

  if (!titulo) return;

  try {
    const res = await fetch('/api/tareas', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        grupo_id: grupoId,
        titulo: titulo,
        fecha_limite: fecha ? fecha : null,
        estado: 'Por iniciar',
        prioridad: 'Media',
      }),
    });
    if (res.ok) {
      inputTitulo.value = '';
      if (inputFecha) inputFecha.value = '';
      Toast.fire({ icon: 'success', title: 'Actividad creada con éxito' });
      setTimeout(() => location.reload(), 350);
    }
  } catch (e) {
    console.error(e);
  }
}

// Eliminar tarea
async function confirmarEliminarTarea(tareaId, event) {
  if (event) event.stopPropagation();
  const result = await Swal.fire({
    title: '¿Eliminar actividad?',
    text: 'Esta acción no se puede deshacer.',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#e2445c',
    cancelButtonColor: '#6c757d',
    confirmButtonText: 'Sí, eliminar',
    cancelButtonText: 'Cancelar',
  });

  if (result.isConfirmed) {
    const res = await fetch(`/api/tareas/${tareaId}`, { method: 'DELETE' });
    if (res.ok) {
      Toast.fire({ icon: 'success', title: 'Actividad eliminada' });
      setTimeout(() => location.reload(), 350);
    }
  }
}

// ==========================================
// DRAG & DROP DINÁMICO DE FILAS EN EL TABLERO
// ==========================================

function initTableDragDrop() {
  const rows = document.querySelectorAll('.tarea-fila');
  const tbodies = document.querySelectorAll('.monday-tbody');
  let draggedRow = null;

  rows.forEach(row => {
    row.addEventListener('dragstart', (e) => {
      draggedRow = row;
      row.classList.add('dragging-row');
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('text/plain', row.getAttribute('data-tarea-id'));
    });

    row.addEventListener('dragend', () => {
      if (draggedRow) {
        draggedRow.classList.remove('dragging-row');
      }
      document.querySelectorAll('.tarea-fila').forEach(r => {
        r.classList.remove('drag-over-top', 'drag-over-bottom');
      });
      document.querySelectorAll('.monday-tbody').forEach(tb => tb.classList.remove('drag-over'));
      draggedRow = null;
    });

    row.addEventListener('dragover', (e) => {
      e.preventDefault();
      if (!draggedRow || draggedRow === row) return;

      const rect = row.getBoundingClientRect();
      const mid = rect.top + rect.height / 2;

      document.querySelectorAll('.tarea-fila').forEach(r => {
        if (r !== row) r.classList.remove('drag-over-top', 'drag-over-bottom');
      });

      if (e.clientY < mid) {
        row.classList.add('drag-over-top');
        row.classList.remove('drag-over-bottom');
      } else {
        row.classList.add('drag-over-bottom');
        row.classList.remove('drag-over-top');
      }
    });

    row.addEventListener('dragleave', () => {
      row.classList.remove('drag-over-top', 'drag-over-bottom');
    });

    row.addEventListener('drop', async (e) => {
      e.preventDefault();
      if (!draggedRow || draggedRow === row) return;

      const targetTbody = row.closest('.monday-tbody');
      const isTop = row.classList.contains('drag-over-top');
      const tareaId = draggedRow.getAttribute('data-tarea-id');
      row.classList.remove('drag-over-top', 'drag-over-bottom');

      if (isTop) {
        targetTbody.insertBefore(draggedRow, row);
      } else {
        const nextTarget = (row.nextElementSibling && row.nextElementSibling.classList.contains('subelementos-contenedor-row'))
          ? row.nextElementSibling.nextSibling
          : row.nextSibling;
        targetTbody.insertBefore(draggedRow, nextTarget);
      }

      const subrow = document.getElementById(`subrow-${tareaId}`);
      if (subrow) {
        draggedRow.after(subrow);
      }

      await guardarNuevoOrdenFila(draggedRow, targetTbody);
    });
  });

  tbodies.forEach(tbody => {
    tbody.addEventListener('dragover', (e) => {
      e.preventDefault();
      tbody.classList.add('drag-over');
    });

    tbody.addEventListener('dragleave', () => {
      tbody.classList.remove('drag-over');
    });

    tbody.addEventListener('drop', async (e) => {
      e.preventDefault();
      tbody.classList.remove('drag-over');
      if (draggedRow && !tbody.contains(draggedRow)) {
        const tareaId = draggedRow.getAttribute('data-tarea-id');
        tbody.appendChild(draggedRow);
        const subrow = document.getElementById(`subrow-${tareaId}`);
        if (subrow) {
          draggedRow.after(subrow);
        }
        await guardarNuevoOrdenFila(draggedRow, tbody);
      }
    });
  });
}

async function guardarNuevoOrdenFila(row, tbody) {
  const tareaId = row.getAttribute('data-tarea-id');
  const nuevoGrupoId = parseInt(tbody.getAttribute('data-grupo-id'));
  const allRows = Array.from(tbody.querySelectorAll('.tarea-fila'));
  const nuevoOrden = allRows.indexOf(row) + 1;

  row.setAttribute('data-grupo-id', nuevoGrupoId);

  try {
    const res = await fetch(`/api/tareas/${tareaId}/mover`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        grupo_id: nuevoGrupoId,
        nuevo_orden: nuevoOrden,
      }),
    });
    if (res.ok) {
      Toast.fire({ icon: 'success', title: 'Fila reubicada correctamente' });
    }
  } catch (err) {
    console.error('Error al mover fila:', err);
  }
}

// ==========================================
// MODAL DETALLE DE TAREA (SUBTAREAS & COMENTARIOS)
// ==========================================

async function verDetalleTarea(tareaId) {
  try {
    const res = await fetch(`/api/tareas/${tareaId}/detalle`);
    if (!res.ok) return;
    const t = await res.json();

    document.getElementById('modalTareaTitulo').value = t.titulo;
    document.getElementById('modalTareaDesc').value = t.descripcion || '';
    document.getElementById('modalTareaResponsable').value = t.responsable || '';
    document.getElementById('modalTareaPuntos').value = t.puntos_historia || 1;
    document.getElementById('modalTareaTipo').value = t.tipo_tarea || 'Tarea';
    document.getElementById('modalTareaFechaInicio').value = t.fecha_inicio || '';
    document.getElementById('modalTareaFechaLimite').value = t.fecha_limite || '';
    document.getElementById('modalTareaId').value = t.id;

    // Renderizar subtareas
    const subContainer = document.getElementById('listaSubtareas');
    subContainer.innerHTML = '';
    if (t.subtareas && t.subtareas.length > 0) {
      t.subtareas.forEach(s => {
        subContainer.innerHTML += `
          <div class="d-flex align-items-center justify-content-between p-2 mb-1 bg-light rounded">
            <div class="form-check">
              <input class="form-check-input" type="checkbox" ${s.completada ? 'checked' : ''} onchange="toggleSubtarea(${s.id})">
              <label class="form-check-label ${s.completada ? 'text-decoration-line-through text-muted' : ''}">${s.titulo}</label>
            </div>
            <button class="btn btn-sm text-danger p-0 border-0" onclick="eliminarSubtarea(${s.id})"><i class="fa fa-trash"></i></button>
          </div>
        `;
      });
    } else {
      subContainer.innerHTML = '<p class="text-muted small">No hay sub-elementos aún.</p>';
    }

    // Renderizar comentarios
    const comContainer = document.getElementById('listaComentarios');
    comContainer.innerHTML = '';
    if (t.comentarios && t.comentarios.length > 0) {
      t.comentarios.forEach(c => {
        comContainer.innerHTML += `
          <div class="border rounded p-2 mb-2 bg-white">
            <div class="d-flex justify-content-between align-items-center mb-1">
              <span class="fw-bold small text-primary"><i class="fa fa-user-circle"></i> ${c.autor}</span>
              <span class="text-muted" style="font-size:0.75rem;">${c.fecha}</span>
            </div>
            <p class="mb-0 small text-dark">${c.contenido}</p>
          </div>
        `;
      });
    } else {
      comContainer.innerHTML = '<p class="text-muted small">Sin actualizaciones registradas.</p>';
    }

    const modal = new bootstrap.Modal(document.getElementById('modalDetalleTarea'));
    modal.show();
  } catch (e) {
    console.error(e);
  }
}

async function guardarCambiosDetalle() {
  const tareaId = document.getElementById('modalTareaId').value;
  const payload = {
    titulo: document.getElementById('modalTareaTitulo').value.trim(),
    descripcion: document.getElementById('modalTareaDesc').value.trim(),
    responsable: document.getElementById('modalTareaResponsable').value.trim(),
    puntos_historia: parseInt(document.getElementById('modalTareaPuntos').value) || 1,
    tipo_tarea: document.getElementById('modalTareaTipo').value,
    fecha_inicio: document.getElementById('modalTareaFechaInicio').value || null,
    fecha_limite: document.getElementById('modalTareaFechaLimite').value || null,
  };

  await actualizarCampoTarea(tareaId, payload);
}

async function agregarSubtareaModal() {
  const tareaId = document.getElementById('modalTareaId').value;
  const input = document.getElementById('inputNuevaSubtarea');
  const titulo = input.value.trim();
  if (!titulo) return;

  const res = await fetch(`/api/tareas/${tareaId}/subtareas`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ titulo: titulo }),
  });
  if (res.ok) {
    input.value = '';
    verDetalleTarea(tareaId);
  }
}

async function toggleSubtarea(subId) {
  const tareaId = document.getElementById('modalTareaId').value;
  await fetch(`/api/subtareas/${subId}/toggle`, { method: 'PATCH' });
  verDetalleTarea(tareaId);
}

async function eliminarSubtarea(subId) {
  const tareaId = document.getElementById('modalTareaId').value;
  await fetch(`/api/subtareas/${subId}`, { method: 'DELETE' });
  verDetalleTarea(tareaId);
}

async function agregarComentarioModal() {
  const tareaId = document.getElementById('modalTareaId').value;
  const autor = document.getElementById('inputAutorComentario').value.trim() || 'Usuario';
  const texto = document.getElementById('inputTextoComentario').value.trim();
  if (!texto) return;

  const res = await fetch(`/api/tareas/${tareaId}/comentarios`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ autor: autor, contenido: texto }),
  });
  if (res.ok) {
    document.getElementById('inputTextoComentario').value = '';
    verDetalleTarea(tareaId);
  }
}

// ==========================================
// DRAG & DROP EN KANBAN
// ==========================================

function initKanbanDragDrop() {
  const cards = document.querySelectorAll('.kanban-card');
  const cols = document.querySelectorAll('.kanban-cards-container');

  cards.forEach(card => {
    card.addEventListener('dragstart', () => {
      card.classList.add('dragging');
    });

    card.addEventListener('dragend', () => {
      card.classList.remove('dragging');
    });
  });

  cols.forEach(col => {
    col.addEventListener('dragover', e => {
      e.preventDefault();
      col.classList.add('bg-light');
    });

    col.addEventListener('dragleave', () => {
      col.classList.remove('bg-light');
    });

    col.addEventListener('drop', async e => {
      e.preventDefault();
      col.classList.remove('bg-light');
      const draggingCard = document.querySelector('.dragging');
      if (draggingCard) {
        col.appendChild(draggingCard);
        const tareaId = draggingCard.getAttribute('data-tarea-id');
        const nuevoEstado = col.getAttribute('data-estado');
        await cambiarEstado(tareaId, nuevoEstado);
      }
    });
  });
}

// ==========================================
// CREAR GRUPO & PROYECTO
// ==========================================

async function crearNuevoGrupo(proyectoId) {
  const { value: titulo } = await Swal.fire({
    title: 'Nuevo Grupo',
    input: 'text',
    inputLabel: 'Nombre del grupo (ej. Fase 1, Próximas Entregas)',
    inputPlaceholder: 'Escribe el nombre...',
    showCancelButton: true,
    confirmButtonText: 'Crear Grupo',
    confirmButtonColor: '#6161FF',
  });

  if (titulo) {
    const res = await fetch('/api/grupos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ proyecto_id: proyectoId, titulo: titulo }),
    });
    if (res.ok) {
      Toast.fire({ icon: 'success', title: 'Grupo creado' });
      setTimeout(() => location.reload(), 400);
    }
  }
}

async function crearNuevoProyecto() {
  const { value: formValues } = await Swal.fire({
    title: 'Crear Nuevo Proyecto',
    html:
      '<input id="swal-prj-nombre" class="swal2-input" placeholder="Nombre del proyecto">' +
      '<input id="swal-prj-clave" class="swal2-input" placeholder="Clave (ej. PROY)">' +
      '<input id="swal-prj-desc" class="swal2-input" placeholder="Descripción breve">',
    focusConfirm: false,
    showCancelButton: true,
    confirmButtonText: 'Crear Proyecto',
    confirmButtonColor: '#6161FF',
    preConfirm: () => {
      return {
        nombre: document.getElementById('swal-prj-nombre').value,
        clave: document.getElementById('swal-prj-clave').value,
        descripcion: document.getElementById('swal-prj-desc').value,
      };
    },
  });

  if (formValues && formValues.nombre) {
    const res = await fetch('/api/proyectos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formValues),
    });
    if (res.ok) {
      const data = await res.json();
      Toast.fire({ icon: 'success', title: 'Proyecto creado' });
      window.location.href = `/tablero?proyecto_id=${data.id}`;
    }
  }
}

// Búsqueda instantánea en tablero
function filtrarTablero(texto) {
  const term = texto.toLowerCase();
  const filas = document.querySelectorAll('.tarea-fila');
  filas.forEach(f => {
    const content = f.textContent.toLowerCase();
    f.style.display = content.includes(term) ? '' : 'none';
  });
}
