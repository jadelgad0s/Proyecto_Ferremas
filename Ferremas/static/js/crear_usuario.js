const togglePassword = document.getElementById('togglePassword');
const passwordInput = document.getElementById('contrasena');
const iconEye = document.getElementById('iconEye');

togglePassword.addEventListener('click', () => {
const isPassword = passwordInput.type === 'password';
passwordInput.type = isPassword ? 'text' : 'password';
iconEye.classList.toggle('bi-eye');
iconEye.classList.toggle('bi-eye-slash');
});