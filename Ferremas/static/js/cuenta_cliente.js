document.addEventListener("DOMContentLoaded", () => {
  // Elementos correo
  const btnEditarCorreo = document.getElementById("btn-editar-correo");
  const btnGuardarCorreo = document.getElementById("btn-guardar-correo");
  const btnCerrarCorreo = document.getElementById("btn-cerrar-correo");
  const textoCorreo = document.getElementById("texto-correo");
  const campoCorreo = document.getElementById("campo-correo");
  
  // Elementos contraseña
  const btnMostrarContrasena = document.getElementById("btn-mostrar-form-contrasena");
  const cambioContrasena = document.getElementById("cambio-contrasena");
  const btnCerrarContrasena = document.getElementById("btn-cerrar-contrasena");
  
  // Input oculto para la acción
  const inputAccion = document.getElementById("input-accion");

  // ---- EDITAR CORREO ----
  btnEditarCorreo.addEventListener("click", () => {
    campoCorreo.classList.remove("d-none");
    textoCorreo.classList.add("d-none");
    btnGuardarCorreo.classList.remove("d-none");
    btnCerrarCorreo.classList.remove("d-none");

    btnEditarCorreo.classList.add("d-none");
    btnMostrarContrasena.classList.add("d-none");

    inputAccion.value = ""; // limpiamos acción hasta guardar
  });

  btnCerrarCorreo.addEventListener("click", () => {
    campoCorreo.classList.add("d-none");
    textoCorreo.classList.remove("d-none");
    btnGuardarCorreo.classList.add("d-none");
    btnCerrarCorreo.classList.add("d-none");

    btnEditarCorreo.classList.remove("d-none");
    btnMostrarContrasena.classList.remove("d-none");

    inputAccion.value = "";
    // Opcional: restaurar el valor original por si escribió algo
    campoCorreo.value = textoCorreo.textContent.trim();
  });

  btnGuardarCorreo.addEventListener("click", () => {
    inputAccion.value = "editar_correo";
    // submit se realiza por botón type="submit"
  });

  // ---- CAMBIAR CONTRASEÑA ----
  btnMostrarContrasena.addEventListener("click", () => {
    cambioContrasena.classList.remove("d-none");

    btnEditarCorreo.classList.add("d-none");
    btnMostrarContrasena.classList.add("d-none");
  });

  btnCerrarContrasena.addEventListener("click", () => {
    cambioContrasena.classList.add("d-none");

    btnEditarCorreo.classList.remove("d-none");
    btnMostrarContrasena.classList.remove("d-none");

    // Opcional: limpiar campos de contraseña
    document.getElementById("nueva_contrasena").value = "";
    document.getElementById("confirmar_contrasena").value = "";
    // Limpiar checkbox mostrar contraseña
    document.getElementById("togglePassword").checked = false;
    document.getElementById("nueva_contrasena").type = "password";
    document.getElementById("confirmar_contrasena").type = "password";
  });

  // ---- TOGGLE CONTRASEÑAS ----
  const togglePassword = document.getElementById("togglePassword");
  togglePassword.addEventListener("change", () => {
    const tipo = togglePassword.checked ? "text" : "password";
    document.getElementById("nueva_contrasena").type = tipo;
    document.getElementById("confirmar_contrasena").type = tipo;
  });
});