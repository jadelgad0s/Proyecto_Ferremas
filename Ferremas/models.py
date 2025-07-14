from django.db import models
import uuid

# Tabla: tipo_usuario
class TipoUsuario(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo_rol = models.CharField(max_length=50)

    def __str__(self):
        return self.tipo_rol

# Tabla: usuarios
class Usuario(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_tipo_usuario = models.ForeignKey(TipoUsuario, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    apellido = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    rut = models.CharField(max_length=12)
    uid_auth = models.UUIDField(blank=True, null=True, unique=True)
    boletin = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

# Tabla: tipo_producto
class TipoProducto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

# Tabla: proveedor
class Proveedor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=15)

    def __str__(self):
        return self.nombre

# Tabla: producto
class Producto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    id_tipo_producto = models.ForeignKey(TipoProducto, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    id_proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

# Tabla: carrito
class Carrito(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) #
    
    # Hacemos id_cliente opcional para soportar usuarios anónimos
    id_cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True) #
    
    # NUEVO CAMPO: para identificar carritos de usuarios anónimos
    session_key = models.CharField(max_length=40, null=True, blank=True, unique=True) 
    
    # Mantenemos tu campo total, pero es mejor calcularlo. Lo actualizaremos en las vistas.
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) #
    created_at = models.DateTimeField(auto_now_add=True) #
    activo = models.BooleanField(default=True) #

    def __str__(self):
        if self.id_cliente:
            return f"Carrito de {self.id_cliente.nombre} {self.id_cliente.apellido}"
        elif self.session_key:
            return f"Carrito de sesión {self.session_key}"
        return f"Carrito {self.id}"

    @property
    def total_calculado(self):
        items = self.carritoitem_set.all() 
        total_val = sum(item.subtotal_calculado for item in items)
        return total_val

class CarritoItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) #
    id_carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE) #
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE) #
    cantidad = models.PositiveIntegerField() #

    def __str__(self):
        return f"{self.cantidad} x {self.id_producto.nombre} en carrito {self.id_carrito.id}"

    @property
    def subtotal_calculado(self):
        return self.cantidad * self.id_producto.precio

# Tabla: pedido
class Pedido(models.Model):
    METODOS_ENTREGA = [
        ('Domicilio', 'Domicilio'),
        ('Retiro en Tienda', 'Retiro en Tienda'),
    ]

    ESTADOS_DESPACHO = [
        ('Pendiente', 'Pendiente'),
        ('Enviado', 'Enviado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fecha = models.DateField()
    estado = models.CharField(max_length=20, default='Pendiente')  # Estado general del pedido
    total_pedido = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    id_cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id_carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)

    # Campos nuevos para Órdenes de Despacho
    metodo_entrega = models.CharField(max_length=50, choices=METODOS_ENTREGA, default='Domicilio')
    estado_despacho = models.CharField(max_length=20, choices=ESTADOS_DESPACHO, default='Pendiente')

    def __str__(self):
        cliente_info = f"{self.id_cliente.nombre} {self.id_cliente.apellido}" if self.id_cliente else "N/A"
        return f"Pedido {self.id} - Cliente: {cliente_info} - Estado: {self.estado}"
    
# Tabla: detalle_pedido
class DetallePedido(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cantidad = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    id_pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)

# Tabla: entrega
class Entrega(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    fecha_entrega = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=[('Por Registrar', 'Por Registrar'), ('Registrado', 'Registrado')], default='Por Registrar')

    def __str__(self):
        return f"Entrega de {self.pedido} - {self.estado}"

# Tabla: metodo_pago
class MetodoPago(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo_pago = models.CharField(max_length=100)

    def __str__(self):
        return self.tipo_pago

# Tabla: estado_pago
class EstadoPago(models.TextChoices):
    PENDIENTE = 'Pendiente', 'Pendiente'
    PAGADO = 'Pagado', 'Pagado'
    RECHAZADO = 'Rechazado', 'Rechazado'

# Tabla: pago
class Pago(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    metodo = models.ForeignKey(MetodoPago, on_delete=models.SET_NULL, null=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20,
        choices=EstadoPago.choices,
        default=EstadoPago.PENDIENTE
    )

# Tabla: region
class Region(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

# Tabla: comuna
class Comuna(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    id_region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

# Tabla: direccion
class Direccion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    calle = models.CharField(max_length=100)
    num_calle = models.CharField(max_length=10)
    id_comuna = models.ForeignKey(Comuna, on_delete=models.CASCADE)
    id_region = models.ForeignKey(Region, on_delete=models.CASCADE)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

# Tabla: sucursal
class Sucursal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.DecimalField(max_digits=15, decimal_places=0)

    def __str__(self):
        return self.nombre

# Tabla: suscriptores
class Suscriptor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class EncuestaSatisfaccion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE)  # Relación 1 a 1 con pedido
    puntaje = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # 1 a 5 estrellas
    comentario = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Encuesta - Pedido {self.pedido.id} - Puntaje: {self.puntaje}"
    
class Promocion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    descuento = models.PositiveIntegerField()  # En porcentaje
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.descuento}%"