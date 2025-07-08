// Ferremas/static/Ferremas/js/comprar.js

// Función para validar RUT Chileno (algoritmo Módulo 11)
function validarRutChileno(rutCompleto) {
  if (!rutCompleto) return false;
  rutCompleto = rutCompleto.replace(/\./g, '').replace('-', '');
  if (!/^[0-9]+[0-9kK]{1}$/.test(rutCompleto)) {
    return false;
  }
  var tmp = rutCompleto.slice(0, -1);
  var digv = rutCompleto.slice(-1).toLowerCase();
  var rut = parseInt(tmp);

  if (isNaN(rut)) return false;

  var M = 0, S = 1;
  for (; rut; rut = Math.floor(rut / 10)) {
    S = (S + rut % 10 * (9 - M++ % 6)) % 11;
  }
  var dvCalculado = S ? (S - 1).toString() : 'k';
  return (dvCalculado === digv);
}

document.addEventListener('DOMContentLoaded', function() {
  const form = document.querySelector('form[action*="comprar"]'); 
  const rutInput = form ? form.querySelector('input[name="rut"]') : null; 
  
  const radioDomicilio = document.getElementById('domicilio');
  const radioRetiro = document.getElementById('retiro');
  const sucursalSelect = form ? form.querySelector('select[name="sucursal"]') : null;
  
  const shippingCostSummaryElement = document.getElementById('shipping-cost-summary');
  const grandTotalSummaryElement = document.getElementById('grand-total-summary');
  
  // 'initialProductsTotalFromDjango' DEBE estar definida en un <script> en el HTML ANTES de este script.
  const initialProductsTotal = (typeof initialProductsTotalFromDjango !== 'undefined' && !isNaN(initialProductsTotalFromDjango)) 
                               ? initialProductsTotalFromDjango 
                               : 0;
  // console.log("Initial Products Total en JS (comprar.js):", initialProductsTotal);

  const costoEnvioFijo = 8000;

  function actualizarResumenPedido() {
    if (!form) return; 
    let costoEnvioActual = 0;
    
    if (radioDomicilio && radioDomicilio.checked) {
        costoEnvioActual = costoEnvioFijo;
    }
    // console.log("Costo de envío seleccionado (comprar.js):", costoEnvioActual);

    if (shippingCostSummaryElement) {
        shippingCostSummaryElement.textContent = `$${costoEnvioActual.toLocaleString('es-CL')}`;
    }
    
    if (grandTotalSummaryElement) {
        let granTotal = initialProductsTotal + costoEnvioActual;
        // console.log("Calculando Gran Total (comprar.js):", initialProductsTotal, "+", costoEnvioActual, "=", granTotal);
        grandTotalSummaryElement.textContent = `$${granTotal.toLocaleString('es-CL', {maximumFractionDigits: 0, minimumFractionDigits: 0})}`;
    }

    let hiddenShippingCostInput = form.querySelector('input[name="costo_envio"]');
    if (!hiddenShippingCostInput) {
        hiddenShippingCostInput = document.createElement('input');
        hiddenShippingCostInput.type = 'hidden';
        hiddenShippingCostInput.name = 'costo_envio';
        form.appendChild(hiddenShippingCostInput);
    }
    hiddenShippingCostInput.value = costoEnvioActual;
  }

  if (radioDomicilio) {
    radioDomicilio.addEventListener('change', function() {
      if (this.checked && sucursalSelect) {
        sucursalSelect.disabled = true; 
        sucursalSelect.value = ""; 
      }
      actualizarResumenPedido();
    });
  }

  if (radioRetiro) {
    radioRetiro.addEventListener('change', function() {
      if (this.checked && sucursalSelect) {
        sucursalSelect.disabled = false; 
      }
      actualizarResumenPedido();
    });
  }
  
  if (form) { 
    if (sucursalSelect && radioDomicilio && radioRetiro) {
        if (radioDomicilio.checked) {
            sucursalSelect.disabled = true;
        } else if (radioRetiro.checked) { 
            sucursalSelect.disabled = false;
        } else if (radioRetiro) { 
            radioRetiro.checked = true; 
            if(sucursalSelect) sucursalSelect.disabled = false;
        } else if (radioDomicilio && sucursalSelect) { // Fallback
             sucursalSelect.disabled = true;
        }
    }
    actualizarResumenPedido(); 

    if (rutInput) {
      form.addEventListener('submit', function(event) {
        actualizarResumenPedido(); 

        let rutValido = validarRutChileno(rutInput.value);
        if (!rutValido) {
          alert('El RUT ingresado no es válido. Formato ejemplo: 12345678-9 (puede incluir puntos y guion).');
          rutInput.focus(); 
          event.preventDefault(); 
          return false;
        }
      });
    }
  }
});