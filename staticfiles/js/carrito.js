

// Estas constantes se esperan que estén definidas globalmente desde el HTML 
// (en el <script> del <head> de productos.html o tu plantilla base)
// const DJANGO_STATIC_URL;
// const URL_AGREGAR_CARRITO;
// const URL_VER_CARRITO;
// const URL_ACTUALIZAR_CANTIDAD;
// const URL_ELIMINAR_ITEM;
// const CSRF_TOKEN;

// --- Elementos del DOM ---
const cartItemsContainer = document.getElementById('cart-items-container');
const cartTotalBadge = document.getElementById('cart-total-badge');
const cartSubtotalSpan = document.getElementById('cart-subtotal');
const cartGrandTotalSpan = document.getElementById('cart-grand-total');
const cartEmptyMessage = document.getElementById('cart-empty-message');
const checkoutButton = document.getElementById('checkout-button');
const notificationToastElement = document.getElementById('notificationToast');
const toastTitleElement = notificationToastElement ? notificationToastElement.querySelector('#toast-title') : null;
const toastBodyElement = notificationToastElement ? notificationToastElement.querySelector('#toast-body') : null;
// Inicializar el Toast de Bootstrap una sola vez si el elemento existe
const bsToast = notificationToastElement ? new bootstrap.Toast(notificationToastElement, { delay: 3000 }) : null;

// URL para una imagen por defecto (asegúrate que esta imagen exista en tus estáticos de Django)
// Se asume que DJANGO_STATIC_URL ya está definida globalmente en el HTML.
// Si tus imágenes estáticas están directamente bajo 'static/img/', usa: DJANGO_STATIC_URL + 'img/placeholder.png'
// Si están en 'static/Ferremas/img/', usa: DJANGO_STATIC_URL + /img/placeholder.png'
// Basado en tu última corrección, tus imágenes están en 'static/img/' 
const DEFAULT_IMAGE_URL = (typeof DJANGO_STATIC_URL !== 'undefined' ? DJANGO_STATIC_URL : '/static/') + 'img/placeholder.png';


function showToast(title, message, type = 'success') {
    if (!bsToast || !toastTitleElement || !toastBodyElement) {
        alert(`${title}: ${message}`); // Fallback si el toast no está configurado
        return;
    }
    toastTitleElement.textContent = title;
    toastBodyElement.textContent = message;
    
    let toastHeader = notificationToastElement.querySelector('.toast-header');
    // Limpiar clases de contexto anteriores del header y del toast mismo
    toastHeader.classList.remove('bg-success', 'bg-danger', 'bg-warning', 'text-white', 'text-dark');
    notificationToastElement.classList.remove('bg-success', 'bg-danger', 'bg-warning');

    if (type === 'success') {
      toastHeader.classList.add('bg-success', 'text-white');
    } else if (type === 'error') {
      toastHeader.classList.add('bg-danger', 'text-white');
    } else if (type === 'warning') {
      toastHeader.classList.add('bg-warning', 'text-dark');
    }
    bsToast.show();
}

async function handleAddToCart(event) {
    const productId = this.dataset.productId; // 'this' se refiere al botón que inicio el evento
    if (!productId) return;

    // Asegurarse que las URLs y Tokens estén disponibles
    if (typeof URL_AGREGAR_CARRITO === 'undefined' || typeof CSRF_TOKEN === 'undefined') {
        console.error('URLs de API o CSRF_TOKEN no definidos.');
        showToast('Error de Configuración', 'No se pueden realizar acciones de carrito.', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('product_id', productId);
    formData.append('cantidad', '1'); // Por defecto se añade 1 unidad

    try {
        const response = await fetch(URL_AGREGAR_CARRITO, {
            method: 'POST',
            headers: {
                'X-CSRFToken': CSRF_TOKEN,
                'X-Requested-With': 'XMLHttpRequest', 
            },
            body: formData,
        });
        const data = await response.json();

        if (response.ok && data.success) {
            showToast('Carrito', data.message || 'Producto añadido al carrito.', 'success');
            if (cartTotalBadge) { 
                cartTotalBadge.textContent = data.cart_total_items;
                cartTotalBadge.style.display = (data.cart_total_items > 0) ? 'inline-block' : 'none';
            }
        } else {
            showToast('Error', data.error || 'No se pudo añadir el producto.', 'error');
        }
    } catch (error) {
        console.error('Error en fetch al añadir al carrito:', error);
        showToast('Error', 'Error de conexión al añadir al carrito.', 'error');
    }
}

async function displayCart() {
    if (!cartItemsContainer || !cartSubtotalSpan || !cartGrandTotalSpan || !cartEmptyMessage || !checkoutButton) {
        return;
    }
    if (typeof URL_VER_CARRITO === 'undefined') {
        console.error('URL_VER_CARRITO no definida.');
        if (cartItemsContainer) cartItemsContainer.innerHTML = '<p class="text-danger">Error de configuración para ver el carrito.</p>';
        return;
    }

    try {
        const response = await fetch(URL_VER_CARRITO); 
        if (!response.ok) {
            throw new Error(`Error HTTP al ver carrito: ${response.status}`);
        }
        const data = await response.json();

        if (cartTotalBadge) { 
             cartTotalBadge.textContent = data.total_items_count || '0';
             cartTotalBadge.style.display = (data.total_items_count > 0) ? 'inline-block' : 'none';
        }
        cartSubtotalSpan.textContent = `$${Number(data.cart_total_value).toLocaleString('es-CL', {minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
        cartGrandTotalSpan.textContent = `$${Number(data.cart_total_value).toLocaleString('es-CL', {minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;

        if (data.items && data.items.length > 0) {
            if(cartEmptyMessage) cartEmptyMessage.style.display = 'none';
            if(checkoutButton) checkoutButton.classList.remove('disabled');
            cartItemsContainer.innerHTML = ''; 
            data.items.forEach(item => {
                const imageUrl = item.imagen_url ? item.imagen_url : DEFAULT_IMAGE_URL; 
                const cartItemHTML = `
                    <div class="d-flex align-items-start mb-3 border-bottom pb-3 cart-item-row" 
                            data-item-id="${item.id}" 
                            data-product-id="${item.product_id}"
                            data-stock="${item.stock_producto}">
                        <img src="${imageUrl}" class="me-2" style="width: 60px; height: 60px; object-fit: contain;" alt="${item.nombre}">
                        <div class="w-100">
                        <p class="mb-1 fw-bold">${item.nombre}</p>
                        <p class="mb-1">$${Number(item.precio).toLocaleString('es-CL', {minimumFractionDigits: 0, maximumFractionDigits: 0 })}</p>
                        <div class="d-flex align-items-center">
                            <span class="me-2">Cantidad</span>
                            <div class="input-group input-group-sm" style="width: 120px;">
                            <button class="btn btn-outline-secondary cart-quantity-change" data-action="decrease" data-itemid="${item.id}">-</button>
                            <input type="number" class="form-control text-center cart-item-quantity-input" value="${item.cantidad}" min="1" max="${item.stock_producto}" data-itemid="${item.id}" style="width: 40px;">
                            <button class="btn btn-outline-secondary cart-quantity-change" data-action="increase" data-itemid="${item.id}">+</button>
                            </div>
                            <button class="btn btn-sm btn-link text-danger ms-auto cart-item-remove" data-itemid="${item.id}"><i class="bi bi-trash"></i></button>
                        </div>
                        </div>
                    </div>
                `;
                cartItemsContainer.insertAdjacentHTML('beforeend', cartItemHTML);
            });
        } else {
            if(cartEmptyMessage) cartEmptyMessage.style.display = 'block';
            if(checkoutButton) checkoutButton.classList.add('disabled');
            cartItemsContainer.innerHTML = ''; 
        }
        attachCartItemEventListeners();
    } catch (error) {
        console.error('Error al mostrar el carrito:', error);
        showToast('Error Carrito', 'No se pudo cargar el contenido del carrito.', 'error');
        if (cartItemsContainer) cartItemsContainer.innerHTML = '<p class="text-danger">Error al cargar el carrito.</p>';
    }
}

function attachCartItemEventListeners() {
    const currentCartItemsContainer = document.getElementById('cart-items-container');
    if (!currentCartItemsContainer) return;

    currentCartItemsContainer.querySelectorAll('.cart-quantity-change').forEach(button => {
        const newBtn = button.cloneNode(true);
        button.parentNode.replaceChild(newBtn, button);
        newBtn.addEventListener('click', handleQuantityButtonClick);
    });

    currentCartItemsContainer.querySelectorAll('.cart-item-remove').forEach(button => {
        const newBtn = button.cloneNode(true);
        button.parentNode.replaceChild(newBtn, button);
        newBtn.addEventListener('click', handleRemoveItemClick);
    });
    
    currentCartItemsContainer.querySelectorAll('.cart-item-quantity-input').forEach(input => {
        const newInput = input.cloneNode(true);
        input.parentNode.replaceChild(newInput, input);
        newInput.addEventListener('change', handleQuantityInputChange);
    });
}

async function handleQuantityButtonClick(event) {
    const itemId = this.dataset.itemid; 
    const action = this.dataset.action;
    const itemRow = this.closest('.cart-item-row');
    if (!itemRow) return;
    const currentQuantityInput = itemRow.querySelector('.cart-item-quantity-input');
    let newQuantity = parseInt(currentQuantityInput.value, 10);
    const stock = parseInt(itemRow.dataset.stock, 10);

    if (action === 'increase') {
        if (newQuantity < stock) {
            newQuantity++;
        } else {
            showToast('Stock', 'No puedes añadir más, stock máximo alcanzado.', 'warning');
            return;
        }
    } else if (action === 'decrease') {
        newQuantity--; 
    }
    await updateCartItemQuantity(itemId, newQuantity);
}

async function handleQuantityInputChange(event) {
    const input = event.target;
    const itemId = input.dataset.itemid; 
    let newQuantity = parseInt(input.value, 10);
    const itemRow = input.closest('.cart-item-row');
    if (!itemRow) return;
    const stock = parseInt(itemRow.dataset.stock, 10);

    if (isNaN(newQuantity) || newQuantity < 0) {
        newQuantity = 0; 
    }
    if (newQuantity > stock) {
        newQuantity = stock;
        input.value = stock; 
        showToast('Stock', `Máximo stock disponible es ${stock}.`, 'warning');
    }
    await updateCartItemQuantity(itemId, newQuantity);
}

async function updateCartItemQuantity(itemId, quantity) {
    if (typeof URL_ACTUALIZAR_CANTIDAD === 'undefined' || typeof CSRF_TOKEN === 'undefined') {
        console.error('URL_ACTUALIZAR_CANTIDAD o CSRF_TOKEN no definidos.');
        showToast('Error de Configuración', 'No se puede actualizar cantidad.', 'error');
        return;
    }

    if (quantity <= 0) { 
        await removeItem(itemId, false); 
        return;
    }

    const formData = new FormData();
    formData.append('item_id', itemId);
    formData.append('cantidad', quantity);

    try {
        const response = await fetch(URL_ACTUALIZAR_CANTIDAD, {
            method: 'POST',
            headers: { 'X-CSRFToken': CSRF_TOKEN, 'X-Requested-With': 'XMLHttpRequest' },
            body: formData,
        });
        const data = await response.json();
        if (response.ok && data.success) {
            showToast('Carrito', data.message || 'Cantidad actualizada.', 'success');
        } else {
            showToast('Error', data.error || 'No se pudo actualizar la cantidad.', 'error');
        }
    } catch (error) {
        console.error('Error al actualizar cantidad:', error);
        showToast('Error', 'Error de conexión al actualizar.', 'error');
    }
    await displayCart(); 
}

async function handleRemoveItemClick(event) {
    const itemId = this.dataset.itemid; 
    await removeItem(itemId);
}

async function removeItem(itemId, showSuccessToast = true) {
    if (typeof URL_ELIMINAR_ITEM === 'undefined' || typeof CSRF_TOKEN === 'undefined') {
        console.error('URL_ELIMINAR_ITEM o CSRF_TOKEN no definidos.');
        showToast('Error de Configuración', 'No se puede eliminar item.', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('item_id', itemId);
    try {
        const response = await fetch(URL_ELIMINAR_ITEM, {
            method: 'POST',
            headers: { 'X-CSRFToken': CSRF_TOKEN, 'X-Requested-With': 'XMLHttpRequest' },
            body: formData,
        });
        const data = await response.json();
        if (response.ok && data.success) {
            if (showSuccessToast) showToast('Carrito', data.message || 'Producto eliminado.', 'success');
        } else {
            showToast('Error', data.error || 'No se pudo eliminar el producto.', 'error');
        }
    } catch (error) {
        console.error('Error al eliminar item:', error);
        showToast('Error', 'Error de conexión al eliminar.', 'error');
    }
    await displayCart(); 
}

// --- Event Listeners Iniciales ---
document.addEventListener('DOMContentLoaded', () => {
    // Verificar si las constantes necesarias están definidas
    if (typeof URL_AGREGAR_CARRITO === 'undefined' || 
        typeof URL_VER_CARRITO === 'undefined' ||
        typeof URL_ACTUALIZAR_CANTIDAD === 'undefined' ||
        typeof URL_ELIMINAR_ITEM === 'undefined' ||
        typeof CSRF_TOKEN === 'undefined' ||
        typeof DJANGO_STATIC_URL === 'undefined') {
        console.error("Alguna de las constantes globales (URLs, CSRF_TOKEN, DJANGO_STATIC_URL) no está definida. Verifica el script en el <head> del HTML.");
        // Podrías mostrar un error más visible al usuario aquí si prefieres
        if (document.body) { // Solo si el body ya existe
             const errorDiv = document.createElement('div');
             errorDiv.innerHTML = '<p style="color: red; text-align: center; font-weight: bold; padding: 10px; background-color: #ffe0e0;">Error de configuración: Faltan variables globales de JavaScript. Revisa la consola.</p>';
             document.body.prepend(errorDiv);
        }
        return; // No continuar si la configuración es incorrecta
    }


    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    addToCartButtons.forEach(button => {
    button.addEventListener('click', function () {
        const card = this.closest('.card');
        const quantityInput = card.querySelector('.quantity-input');
        const cantidad = quantityInput ? parseInt(quantityInput.value) || 1 : 1;

        handleAddToCartWithQuantity(this.dataset.productId, cantidad);
    });
    });

    const offcanvasCarritoElement = document.getElementById('offcanvasCarrito');
    if (offcanvasCarritoElement) {
        offcanvasCarritoElement.addEventListener('show.bs.offcanvas', function () {
            displayCart(); 
        });
    }
    // Mostrar el carrito al cargar la página si el offcanvas está abierto
    if (offcanvasCarritoElement && offcanvasCarritoElement.classList.contains('show')) {
        displayCart(); 
    }
    // Mostrar el carrito al cargar la página
    displayCart();
    // Asegurarse de que los elementos del carrito tengan los listeners adecuados
    attachCartItemEventListeners();
    
});

function initQuantityButtons() {
  const quantityGroups = document.querySelectorAll('.quantity-group');

  quantityGroups.forEach(group => {
    const input = group.querySelector('.quantity-input');
    const btnDecrease = group.querySelector('.quantity-decrease');
    const btnIncrease = group.querySelector('.quantity-increase');

    if (!input || !btnDecrease || !btnIncrease) return;

    btnDecrease.addEventListener('click', () => {
      let currentValue = parseInt(input.value, 10) || 1;
      if (currentValue > 1) {
        input.value = currentValue - 1;
      }
    });

    btnIncrease.addEventListener('click', () => {
      let currentValue = parseInt(input.value, 10) || 1;
      input.value = currentValue + 1;
    });

    input.addEventListener('input', () => {
      let val = input.value.replace(/\D/g, '');
      if (val === '' || parseInt(val) < 1) val = '1';
      input.value = val;
    });
  });
}

// Ejecutar al cargar el DOM
document.addEventListener('DOMContentLoaded', initQuantityButtons);

async function handleAddToCartWithQuantity(productId, cantidad) {
  if (!productId) return;

  const formData = new FormData();
  formData.append('product_id', productId);
  formData.append('cantidad', cantidad);

  try {
    const response = await fetch(URL_AGREGAR_CARRITO, {
      method: 'POST',
      headers: {
        'X-CSRFToken': CSRF_TOKEN,
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: formData,
    });
    const data = await response.json();

    if (response.ok && data.success) {
      showToast('Carrito', data.message || 'Producto añadido al carrito.', 'success');
      if (cartTotalBadge) {
        cartTotalBadge.textContent = data.cart_total_items;
        cartTotalBadge.style.display = (data.cart_total_items > 0) ? 'inline-block' : 'none';
      }
    } else {
      showToast('Error', data.error || 'No se pudo añadir el producto.', 'error');
    }
  } catch (error) {
    console.error('Error al agregar al carrito:', error);
    showToast('Error', 'No se pudo conectar con el servidor.', 'error');
  }
}
