const API_URL = '/api/productos/';

// Cargar productos al iniciar
document.addEventListener('DOMContentLoaded', cargarProductos);

// Cargar productos desde la API
function cargarProductos() {
  fetch(API_URL)
    .then(response => response.json())
    .then(data => renderProductos(data))
    .catch(error => console.error('Error al cargar productos:', error));
}

// Renderizar productos en la tabla
function renderProductos(productos) {
  const tbody = document.querySelector('#tabla-productos tbody');
  tbody.innerHTML = '';

  productos.forEach(prod => {
    const tr = document.createElement('tr');

    tr.innerHTML = `
      <td>
        ${prod.imagen_url ? `<img src="${prod.imagen_url}" alt="imagen" style="max-width: 60px;">` : '-'}
      </td>
      <td>${prod.nombre}</td>
      <td>
        <input type="number" class="form-control form-control-sm text-end" value="${prod.precio}" 
               onchange="actualizarProducto('${prod.id}', 'precio', this.value)">
      </td>
      <td>
        <input type="number" class="form-control form-control-sm text-center" value="${prod.stock}" 
               onchange="actualizarProducto('${prod.id}', 'stock', this.value)">
      </td>
      <td>
        <button class="btn btn-sm btn-danger" onclick="eliminarProducto('${prod.id}')">
          <i class="bi bi-trash"></i>
        </button>
      </td>
    `;

    tbody.appendChild(tr);
  });
}

// Actualizar campo (precio o stock)
function actualizarProducto(id, campo, valor) {
  fetch(`${API_URL}${id}/`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ [campo]: valor })
  })
    .then(res => {
      if (!res.ok) throw new Error('No se pudo actualizar');
      return res.json();
    })
    .then(() => cargarProductos())
    .catch(error => console.error('Error al actualizar:', error));
}

// Eliminar producto
function eliminarProducto(id) {
  if (!confirm('¿Seguro que deseas eliminar este producto?')) return;

  fetch(`${API_URL}${id}/`, { method: 'DELETE' })
    .then(res => {
      if (!res.ok) throw new Error('No se pudo eliminar');
      cargarProductos();
    })
    .catch(error => console.error('Error al eliminar:', error));
}

// Crear nuevo producto
document.getElementById('form-nuevo-producto').addEventListener('submit', function (e) {
  e.preventDefault();

  const form = this;
  if (!form.checkValidity()) {
    form.classList.add('was-validated');
    return;
  }

  const formData = new FormData(form);
  const data = {
    nombre: formData.get('nombre'),
    precio: parseFloat(formData.get('precio')),
    stock: parseInt(formData.get('stock')),
    imagen_url: formData.get('imagen_url'),
    id_tipo_producto: formData.get('id_tipo_producto'),
    id_proveedor: formData.get('id_proveedor')
  };

  // Para verificar que se envía correctamente
  console.log('Enviando producto:', data);

  fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
    .then(res => {
      if (!res.ok) throw new Error('No se pudo crear el producto');
      return res.json();
    })
    .then(() => {
      form.reset();
      form.classList.remove('was-validated');
      cargarProductos();
    })
    .catch(error => {
      console.error('Error al crear producto:', error);
      alert('Hubo un problema al crear el producto. Revisa los datos ingresados.');
    });
});

