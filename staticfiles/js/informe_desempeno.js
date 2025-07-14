document.addEventListener("DOMContentLoaded", () => {
  const btnGenerar = document.querySelector(".btn-outline-primary");
  const resultadoDiv = document.getElementById("resultadoInforme");

  btnGenerar.addEventListener("click", () => {
    const usarSucursal = document.getElementById("filtroSucursal").checked;
    const usarPeriodo = document.getElementById("filtroPeriodo").checked;

    let sucursal = "Todas";
    let periodo = "Ultimos 30 Dias";

    if (usarSucursal) {
      sucursal = document.querySelector("#filtroSucursal + select").value;
    }

    if (usarPeriodo) {
      periodo = document.querySelector("#filtroPeriodo + select").value;
    }

    resultadoDiv.innerHTML = `<p class="text-muted">Cargando informe...</p>`;

    fetch(`/api/informe_desempeno/?sucursal=${sucursal}&periodo=${periodo}`)
      .then(response => {
        if (!response.ok) {
          throw new Error("Respuesta no válida del servidor");
        }
        return response.json();
      })
      .then(data => {
        const html = `
          <h5 class="fw-bold text-center mb-4">Documento Venta Mensual</h5>
          <table class="table">
            <thead class="table-light">
              <tr><th>Información</th><th>Resultados</th></tr>
            </thead>
            <tbody>
              <tr><td>Nivel de Satisfacción Cliente:</td><td>${data.satisfaccion}</td></tr>
              <tr><td>Tiempo Promedio Entrega:</td><td>${data.tiempo_entrega}</td></tr>
              <tr><td>Pedidos Completados:</td><td>${data.completados}</td></tr>
            </tbody>
          </table>
          <div class="text-end mt-3">
            <button id="descargarPDF" class="btn btn-outline-secondary">
              <i class="bi bi-download me-1"></i> Descargar PDF
            </button>
          </div>
        `;
        resultadoDiv.innerHTML = html;

        const descargarBtn = document.getElementById("descargarPDF");
        if (descargarBtn) {
          descargarBtn.addEventListener("click", () => generarPDF(resultadoDiv));
        }
      })
      .catch(error => {
        console.error("Error al obtener datos:", error);
        resultadoDiv.innerHTML = `<p class="text-danger">Error al cargar el informe.</p>`;
      });
  });
});

function generarPDF(elemento) {
  const opciones = {
    margin: 0.5,
    filename: "Informe_Desempeño_Sucursal.pdf",
    image: { type: "jpeg", quality: 0.98 },
    html2canvas: { scale: 2 },
    jsPDF: { unit: "in", format: "letter", orientation: "portrait" }
  };

  html2pdf().from(elemento).set(opciones).save();
}