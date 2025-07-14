document.addEventListener('DOMContentLoaded', () => {
  const tbody = document.getElementById('usuarios-body');
  tbody.innerHTML = '';

  fetch('/api/usuarios_existentes/')
    .then(response => {
      if (!response.ok) {
        throw new Error('Error al obtener los usuarios.');
      }
      return response.json();
    })
    .then(usuarios => {
      if (usuarios.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="4" class="text-center text-muted">No hay usuarios registrados.</td>
          </tr>
        `;
        return;
      }

      usuarios.forEach(usuario => {
        const fila = document.createElement('tr');
        fila.innerHTML = `
          <td>${usuario.nombre}</td>
          <td>${usuario.email}</td>
          <td>${usuario.rol.charAt(0).toUpperCase() + usuario.rol.slice(1)}</td>
          <td>
            <div class="d-flex gap-2">
              <button class="btn btn-sm btn-outline-danger" title="Eliminar" onclick="eliminarUsuario('${usuario.id}')">
                <i class="bi bi-trash"></i>
              </button>
              <a href="/editar_usuario/${usuario.id}/" class="btn btn-sm btn-outline-secondary" title="Editar">
                <i class="bi bi-pencil-square"></i>
              </a>
            </div>
          </td>
        `;
        tbody.appendChild(fila);
      });
    })
    .catch(error => {
      console.error(error);
      tbody.innerHTML = `
        <tr>
          <td colspan="4" class="text-center text-danger">Error al cargar usuarios.</td>
        </tr>
      `;
    });
});

// Función para obtener el token CSRF de la cookie (para Django)
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const c = cookie.trim();
      if (c.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(c.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Función para eliminar usuario usando fetch DELETE a la API REST
function eliminarUsuario(id) {
  if (!confirm('¿Seguro que quieres eliminar este usuario?')) return;

  fetch(`/api/usuarios/${id}/editar/eliminar/`, {
    method: 'DELETE',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
    }
  })
  .then(response => {
    if (response.ok) {
      alert('Usuario eliminado correctamente');
      location.reload();  // recarga la página para actualizar la lista
    } else {
      alert('Error al eliminar usuario');
    }
  })
  .catch(() => alert('Error de conexión'));
}