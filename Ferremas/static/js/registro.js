function toggleRegisterPassword() {
  
  const passwordField = document.getElementById('password');
  const confirmField = document.getElementById('confirmar');

  if (!passwordField || !confirmField) {
    console.error("No se encontraron los campos password o confirmar");
    return;
  }

  const isPassword = passwordField.type === 'password';

  passwordField.type = isPassword ? 'text' : 'password';
  confirmField.type = isPassword ? 'text' : 'password';
}

document.addEventListener('DOMContentLoaded', function () {
  const form = document.querySelector('form');
  form.addEventListener('submit', function (event) {
    const pass1 = document.getElementById('registerPassword').value;
    const pass2 = document.getElementById('registerConfirmar').value;

    if (pass1 !== pass2) {
      alert('Las contraseñas no coinciden.');
      event.preventDefault(); // Evita que se envíe el formulario
    }
  });
});

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('registro-form');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const nombre = document.getElementById('nombre').value.trim();
    const apellidos = document.getElementById('apellidos').value.trim();
    const rut = document.getElementById('rut').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();
    const confirmar = document.getElementById('confirmar').value.trim();

    try {
      const response = await fetch('/api/registro/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
          nombre,
          apellidos,
          rut,
          email,
          password,
          confirmar,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        alert('Registro exitoso. Ahora puedes iniciar sesión.');
        window.location.href = '/login/'; // o a la ruta que quieras
      } else {
        alert(data.error || 'Error en el registro.');
      }
    } catch (error) {
      alert('Error de conexión con el servidor.');
    }
  });

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (const cookie of cookies) {
        const cookieTrim = cookie.trim();
        if (cookieTrim.startsWith(name + '=')) {
          cookieValue = decodeURIComponent(cookieTrim.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});

