from django.contrib import admin
from .models import *

# Registro de modelos
admin.site.register(TipoUsuario)
admin.site.register(Usuario)
admin.site.register(TipoProducto)
admin.site.register(Proveedor)
admin.site.register(Producto)
admin.site.register(Carrito)
admin.site.register(CarritoItem)
admin.site.register(Pedido)
admin.site.register(DetallePedido)
admin.site.register(MetodoPago)
admin.site.register(Pago)
admin.site.register(Region)
admin.site.register(Comuna)
admin.site.register(Direccion)
admin.site.register(Sucursal)
admin.site.register(Suscriptor)
