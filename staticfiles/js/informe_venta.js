document.addEventListener("DOMContentLoaded", function () {
  const btnGenerar = document.querySelector('.btn-outline-primary');
  const filtroMes = document.getElementById('filtroMes');
  const filtroAño = document.getElementById('filtroAño');
  const mesSelect = document.querySelector('select:nth-of-type(1)');
  const añoSelect = document.querySelector('select:nth-of-type(2)');
  const resultadoDiv = document.getElementById('resultadoInforme');

  btnGenerar.addEventListener('click', function () {
    if (!filtroMes.checked || !filtroAño.checked) {
      alert('Debes seleccionar tanto mes como año para generar el informe.');
      return;
    }

    const mes = mesSelect.selectedIndex + 1;
    const año = añoSelect.value;

    fetch(generarInformeURL, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: `mes=${mes}&año=${año}`
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        const resumen = data.data;
        resultadoDiv.innerHTML = `
          <p><strong>Mes:</strong> ${resumen.mes}</p>
          <p><strong>Año:</strong> ${resumen.año}</p>
          <p><strong>Total de Ventas:</strong> $${resumen.total_ventas.toLocaleString()}</p>
          <p><strong>Número de Pedidos:</strong> ${resumen.total_pedidos}</p>
        `;
      } else {
        resultadoDiv.innerHTML = `<p class="text-danger">No se pudo generar el informe.</p>`;
      }
    })
    .catch(error => {
      resultadoDiv.innerHTML = `<p class="text-danger">Error: ${error}</p>`;
    });
  });
});
