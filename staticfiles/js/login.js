function toggleRegisterPassword() {
  const passwordField = document.getElementById('password');

  if (!passwordField) {
    console.error("No se encontraron los campos password o confirmar");
    return;
  }

  const isPassword = passwordField.type === 'password';

  passwordField.type = isPassword ? 'text' : 'password';
}

document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('login-form');
  const errorMessageDiv = document.getElementById('error-message');

  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();

    try {
      const response = await fetch('/api/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('access_token', data.access_token);
        const tipo_usuario = data.usuario_rol;
        
         if (tipo_usuario === 'Cliente') {
          window.location.href = '/index/';
        } else if (tipo_usuario === 'Administrador') {
          window.location.href = '/administrador/';
        } else if (tipo_usuario === 'Vendedor') {
          window.location.href = '/vendedor/';
        } else if (tipo_usuario === 'Bodeguero') {
          window.location.href = '/bodeguero/';
        } else if (tipo_usuario === 'Contador') {
          window.location.href = '/contador/';
        }

        console.log('Respuesta del login:', data);

      } else {
        errorMessageDiv.textContent = data.error || 'Error al iniciar sesión.';
      }
    } catch (error) {
      errorMessageDiv.textContent = 'Error de conexión al servidor.';
    }
  });

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
});