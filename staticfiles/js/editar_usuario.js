

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('form-editar-usuario');
  const usuarioId = form.dataset.id;

  form.addEventListener('submit', async function(event) {
    event.preventDefault();

    const data = {
      nombre: form.nombre.value.trim(),
      apellido: form.apellido.value.trim(),
      email: form.email.value.trim(),
      rut: form.rut.value.trim(),
      rol: form.rol.value
    };

    try {
      const response = await fetch(`/api/usuarios/${usuarioId}/editar/eliminar/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
      });

      const result = await response.json();

      if (response.ok) {
        alert(result.message || 'Usuario actualizado correctamente');
        window.location.href = "/usuarios_existentes/"; // Ajusta si tu ruta es diferente
      } else {
        alert(result.error || 'Error al actualizar usuario');
      }

    } catch (error) {
      alert('Error de conexión');
    }
  });
});

// Función para obtener el token CSRF
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}