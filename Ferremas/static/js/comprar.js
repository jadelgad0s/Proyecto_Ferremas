// --- Función para validar RUT chileno ---
function validarRutChileno(rutCompleto) {
  if (!rutCompleto) return false;
  rutCompleto = rutCompleto.replace(/\./g, '').replace('-', '');
  if (!/^[0-9]+[0-9kK]{1}$/.test(rutCompleto)) return false;

  let cuerpo = rutCompleto.slice(0, -1);
  let dv = rutCompleto.slice(-1).toLowerCase();
  let suma = 0, multiplo = 2;

  for (let i = cuerpo.length - 1; i >= 0; i--) {
    suma += parseInt(cuerpo.charAt(i)) * multiplo;
    multiplo = multiplo < 7 ? multiplo + 1 : 2;
  }

  let dvEsperado = 11 - (suma % 11);
  dvEsperado = dvEsperado === 11 ? '0' : dvEsperado === 10 ? 'k' : dvEsperado.toString();

  return dv === dvEsperado;
}

// --- Función para actualizar costo de envío y total ---
function actualizarResumenPedido() {
  const form = document.getElementById("form-compra");
  const shippingCostElement = document.getElementById("shipping-cost-summary");
  const grandTotalElement = document.getElementById("grand-total-summary");

  const retiro = document.getElementById("retiro");
  const domicilio = document.getElementById("domicilio");
  const sucursalSelect = form.querySelector("select[name='sucursal']");
  const costoEnvioFijo = 8000;

  let costoEnvio = domicilio && domicilio.checked ? costoEnvioFijo : 0;
  let total = (typeof initialProductsTotalFromDjango !== 'undefined' ? initialProductsTotalFromDjango : 0) + costoEnvio;

  if (shippingCostElement) {
    shippingCostElement.textContent = `$${costoEnvio.toLocaleString('es-CL')}`;
  }
  if (grandTotalElement) {
    grandTotalElement.textContent = `$${total.toLocaleString('es-CL', { minimumFractionDigits: 0 })}`;
  }

  // Campo oculto para el costo de envío
  let hiddenInput = form.querySelector("input[name='costo_envio']");
  if (!hiddenInput) {
    hiddenInput = document.createElement('input');
    hiddenInput.type = 'hidden';
    hiddenInput.name = 'costo_envio';
    form.appendChild(hiddenInput);
  }
  hiddenInput.value = costoEnvio;

  // Habilitar / deshabilitar selector de sucursal
  if (sucursalSelect) {
    sucursalSelect.disabled = domicilio && domicilio.checked;
    if (domicilio && domicilio.checked) {
      sucursalSelect.value = "";
    }
  }
}

// --- Cargar comunas dinámicamente ---
function cargarComunasPorRegion(regionSelectId, comunaSelectId) {
  const regionSelect = document.getElementById(regionSelectId);
  const comunaSelect = document.getElementById(comunaSelectId);

  if (!regionSelect || !comunaSelect) return;

  regionSelect.addEventListener("change", async () => {
    const regionId = regionSelect.value;
    comunaSelect.innerHTML = '<option value="">Cargando comunas...</option>';

    if (!regionId) return;

    try {
      const response = await fetch(`/api/comunas/${regionId}/`);
      if (!response.ok) throw new Error("No se pudo cargar comunas");

      const comunas = await response.json();
      comunaSelect.innerHTML = '<option value="">Seleccione comuna</option>';
      comunas.forEach(comuna => {
        const option = document.createElement("option");
        option.value = comuna.id;
        option.textContent = comuna.nombre;
        comunaSelect.appendChild(option);
      });
    } catch (error) {
      comunaSelect.innerHTML = '<option value="">Error al cargar comunas</option>';
      console.error(error);
    }
  });

  // Si hay una región preseleccionada, dispara evento para cargar comunas al editar
  if (regionSelect.value) {
    regionSelect.dispatchEvent(new Event("change"));
  }
}

// --- Inicio ---
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("form-compra");
  const rutInput = form ? form.querySelector("input[name='rut']") : null;

  actualizarResumenPedido();
  cargarComunasPorRegion("region", "comuna");

  // Validación de RUT en envío de formulario
  if (rutInput && form) {
    form.addEventListener("submit", (e) => {
      const rutValido = validarRutChileno(rutInput.value);
      if (!rutValido) {
        e.preventDefault();
        alert("El RUT ingresado no es válido. Formato ejemplo: 12345678-9");
        rutInput.focus();
      }
    });
  }

  // Listeners para cambiar método de envío
  const domicilio = document.getElementById("domicilio");
  const retiro = document.getElementById("retiro");

  if (domicilio) domicilio.addEventListener("change", actualizarResumenPedido);
  if (retiro) retiro.addEventListener("change", actualizarResumenPedido);
});
