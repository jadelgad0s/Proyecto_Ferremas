# Ferremas/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count
from datetime import date, timedelta
from django.db.models import Q
from .supabase_cliente import supabase
from django.contrib import messages
from django.contrib.messages import get_messages
from .models import *
from django.views.decorators.cache import never_cache
from .decoradores import rol_requerido
from django.db.models import Prefetch
import calendar
from django.db.models.functions import TruncMonth
from django.db.models import Avg, F, ExpressionWrapper, DurationField
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction  # Útil para rollback si algo falla
from decimal import Decimal, InvalidOperation
#from transbank.webpay.webpay_plus.transaction import Transaction as WebpayTransaction # Renombrado para evitar conflicto con django.db.transaction
#from transbank.common.integration_type import IntegrationType
from django.conf import settings # Para acceder a las credenciales de settings.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Usuario
from supabase import create_client
from django.conf import settings



@rol_requerido(['Administrador'])
def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    tipos_usuario = TipoUsuario.objects.all()

    return render(request, 'web/editar_usuario.html', {
        'usuario': usuario,
        'tipos_usuario': tipos_usuario,
    })


class EditarEliminarUsuarioApiView(APIView):
    def get(self, request, id):
        usuario = get_object_or_404(Usuario, id=id)
        data = {
            "id": str(usuario.id),
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "email": usuario.email,
            "rut": usuario.rut,
            "rol": usuario.id_tipo_usuario.id if usuario.id_tipo_usuario else None,
        }
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, id):

        usuario = get_object_or_404(Usuario, id=id)

        data = request.data
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        email = data.get('email')
        rut = data.get('rut')
        tipo_rol_id = data.get('rol')

        # Validar campos obligatorios
        if not all([nombre, apellido, email, rut, tipo_rol_id]):
            return Response({"error": "Todos los campos son obligatorios."}, status=status.HTTP_400_BAD_REQUEST)

        # Validar rut
        if not validar_rut(rut):
            return Response({"error": "RUT inválido."}, status=status.HTTP_400_BAD_REQUEST)

        # Validar que no exista otro usuario con mismo rut o email
        if Usuario.objects.exclude(id=usuario.id).filter(rut=rut).exists():
            return Response({"error": "Este RUT ya está registrado por otro usuario."}, status=status.HTTP_400_BAD_REQUEST)

        if Usuario.objects.exclude(id=usuario.id).filter(email=email).exists():
            return Response({"error": "Este correo ya está registrado por otro usuario."}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener tipo usuario
        tipo_usuario = get_object_or_404(TipoUsuario, id=tipo_rol_id)

        # Actualizar usuario
        usuario.nombre = nombre
        usuario.apellido = apellido
        usuario.email = email
        usuario.rut = rut
        usuario.id_tipo_usuario = tipo_usuario
        usuario.save()

        return Response({"message": "Usuario actualizado correctamente."}, status=status.HTTP_200_OK)

    def delete(self, request, id):
        usuario = get_object_or_404(Usuario, id=id)

        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

        uid_auth = usuario.uid_auth 
        print("UID Auth del usuario:", uid_auth)  # Debug

        # Primero intentamos eliminar en Supabase Auth
        if uid_auth:
            try:
                print("Intentando eliminar usuario en Supabase Auth...")
                supabase.auth.admin.delete_user(str(uid_auth))  # Convertir a string
                print("Usuario eliminado en Supabase Auth.")
            except Exception as e:
                print(f"Error eliminando en Supabase Auth: {e}")
                return Response({
                    "error": f"No se pudo eliminar el usuario en Supabase Auth: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Luego eliminamos el usuario localmente
        usuario.delete()

        return Response({"message": "Usuario eliminado correctamente."}, status=status.HTTP_204_NO_CONTENT)


@rol_requerido(['Administrador'])
def usuarios_existentes(request):
    return render(request, 'web/usuarios_existentes.html')

class UsuariosExistentesApiView(APIView):

    def get(self, request):
        usuarios = Usuario.objects.select_related('id_tipo_usuario').all()

        lista_usuarios = []
        for usuario in usuarios:
            lista_usuarios.append({
                'id': usuario.id,
                'nombre': usuario.nombre,
                'apellido': usuario.apellido,
                'email': usuario.email,
                'rut': usuario.rut,
                'rol': usuario.id_tipo_usuario.tipo_rol,
                'id-auth': usuario.uid_auth
            })

        return Response(lista_usuarios, status=status.HTTP_200_OK)

def pagina_registro(request):
    return render(request, 'web/registro.html')

class RegistroApiView(APIView):

    def post(self, request):
        data = request.data
        nombre = data.get('nombre')
        apellido = data.get('apellidos')
        rut = data.get('rut')
        email = data.get('email')
        password = data.get('password')
        confirmar = data.get('confirmar')

        # Validaciones básicas
        if not all([nombre, apellido, rut, email, password, confirmar]):
            return Response({"error": "Debe completar todos los campos."}, status=status.HTTP_400_BAD_REQUEST)

        if len(nombre) < 3 or len(nombre) > 50:
            return Response({"error": "El nombre debe tener al menos 3 caracteres"}, status=status.HTTP_400_BAD_REQUEST)

        if len(apellido) < 3 or len(apellido) > 50:
            return Response({"error": "El apellido debe tener al menos 3 caracteres"}, status=status.HTTP_400_BAD_REQUEST)

        if password != confirmar:
            return Response({"error": "Las contraseñas no coinciden."}, status=status.HTTP_400_BAD_REQUEST)

        if not validar_rut(rut):
            return Response({"error": "RUT inválido. Por favor Verifica el formato Ej: 12345678-9"}, status=status.HTTP_400_BAD_REQUEST)

        if Usuario.objects.filter(rut=rut).exists():
            return Response({"error": "Este Rut ya esta registrado"}, status=status.HTTP_400_BAD_REQUEST)
        
        if Usuario.objects.filter(email=email).exists():
            return Response({"error": "Este correo ya esta registrado"}, status=status.HTTP_400_BAD_REQUEST)

        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

        try:
            auth_response = supabase.auth.sign_up({
                'email': email,
                'password': password
            })

            if auth_response.user is None:
                return Response({"error": "No se pudo registrar en auth supabase."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": f"Error con Supabase: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        tipo_cliente, _ = TipoUsuario.objects.get_or_create(tipo_rol="Cliente")
        usuario = Usuario.objects.create(
            nombre=nombre,
            apellido=apellido,
            email=email,
            rut=rut,
            id_tipo_usuario=tipo_cliente,
            uid_auth=auth_response.user.id
        )

        return Response({"message": "Cuenta creada con éxito. Verifica tu correo electronico ."}, status=status.HTTP_201_CREATED)


def pagina_login(request):
    return render(request, 'web/login.html')

class LoginApiView(APIView):
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

        try:
            auth_response = supabase.auth.sign_in_with_password({
                'email': email,
                'password': password
            })

            if auth_response.user and auth_response.session:
                try:
                    usuario = Usuario.objects.get(email=email)
                    rol = usuario.id_tipo_usuario.tipo_rol

                    # Guardar datos en sesión con las claves correctas
                    request.session['user_email'] = usuario.email
                    request.session['usuario_id'] = str(usuario.id)
                    request.session['usuario_nombre'] = usuario.nombre
                    request.session['usuario_rol'] = rol
                    request.session['logueado'] = True
                    request.session['access_token'] = auth_response.session.access_token
                    request.session['refresh_token'] = auth_response.session.refresh_token

                    return Response({
                        'email': email,
                        'usuario_id': str(usuario.id),
                        'usuario_nombre': usuario.nombre,
                        'usuario_rol': rol,
                        'access_token': auth_response.session.access_token,
                        'refresh_token': auth_response.session.refresh_token
                    }, status=status.HTTP_200_OK)

                except Usuario.DoesNotExist:
                    return Response({'error': 'No tienes un perfil en la base de datos.'}, status=status.HTTP_404_NOT_FOUND)

            else:
                return Response({'error': 'Correo o contraseña incorrectos.'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': 'Correo o contraseña inválidos.'}, status=status.HTTP_400_BAD_REQUEST)


def index(request):
    # Limpiar mensajes previos (fuerza a consumirlos)
    list(get_messages(request))

    cart = _get_or_create_cart(request)
    cart_items_count = 0
    if cart:
        result = CarritoItem.objects.filter(id_carrito=cart).aggregate(total_cantidad=Sum('cantidad'))
        cart_items_count = result['total_cantidad'] if result['total_cantidad'] is not None else 0

    productos_destacados = Producto.objects.all().order_by('-id')[:6]

    return render(request, 'web/index.html', {
        'cart_items_count': cart_items_count,
        'productos': productos_destacados
    })

def _get_or_create_cart(request):
    cart = None
    cliente_actual = None
    session_key_actual = request.session.session_key
    if not session_key_actual: # Asegurar que siempre haya una session_key
        request.session.create()
        session_key_actual = request.session.session_key

    print(f"DEBUG _get_or_create_cart: Iniciando. Session key actual: {session_key_actual}")

    if 'usuario_id' in request.session:
        try:
            cliente_actual = Usuario.objects.get(id=request.session['usuario_id']) #
            print(f"DEBUG _get_or_create_cart: Usuario encontrado en sesión: {cliente_actual.email}") #

            # 1. Buscar carrito activo del usuario
            cart = Carrito.objects.filter(id_cliente=cliente_actual, activo=True).first() #

            if cart:
                print(f"DEBUG _get_or_create_cart: Carrito encontrado para usuario {cliente_actual.email}, ID Carrito: {cart.id}")
            else:
                print(f"DEBUG _get_or_create_cart: No se encontró carrito activo para {cliente_actual.email}, creando uno nuevo.")
                cart = Carrito.objects.create(id_cliente=cliente_actual, activo=True, total=0.00) #
                print(f"DEBUG _get_or_create_cart: Nuevo carrito creado para usuario {cliente_actual.email}, ID Carrito: {cart.id}")

            # 2. Lógica de Fusión (si el usuario se acaba de loguear y tenía un carrito de sesión)
            session_key_anterior_para_fusion = request.session.get('previous_session_key_before_login')
            if session_key_anterior_para_fusion:
                print(f"DEBUG _get_or_create_cart: Buscando carrito de sesión anterior {session_key_anterior_para_fusion} para fusionar.")
                try:
                    session_cart = Carrito.objects.filter(
                        session_key=session_key_anterior_para_fusion,
                        activo=True,
                        id_cliente__isnull=True
                    ).first()

                    if session_cart and session_cart.id != cart.id: # Asegurarse que no sea el mismo carrito
                        print(f"DEBUG _get_or_create_cart: Fusionando carrito de sesión {session_cart.id} con carrito de usuario {cart.id}")
                        for item_sesion in session_cart.carritoitem_set.all():
                            item_usuario, item_created = CarritoItem.objects.get_or_create(
                                id_carrito=cart, #
                                id_producto=item_sesion.id_producto, #
                                defaults={'cantidad': 0}
                            )
                            cantidad_nueva_total = item_usuario.cantidad + item_sesion.cantidad #
                            if cantidad_nueva_total <= item_sesion.id_producto.stock: #
                                item_usuario.cantidad = cantidad_nueva_total #
                            else:
                                item_usuario.cantidad = item_sesion.id_producto.stock #
                            item_usuario.save()
                        
                        session_cart.delete() # Eliminar el carrito de sesión después de fusionar
                        print(f"DEBUG _get_or_create_cart: Carrito de sesión {session_cart.id} fusionado y eliminado.")
                        
                        # Limpiar la clave de sesión para que no se intente fusionar de nuevo
                        if 'previous_session_key_before_login' in request.session:
                           del request.session['previous_session_key_before_login']
                except Carrito.DoesNotExist:
                    print(f"DEBUG _get_or_create_cart: No se encontró carrito de sesión anterior {session_key_anterior_para_fusion} para fusionar.")
                    pass # No había carrito de sesión para fusionar
            
            # Asegurar que el carrito del usuario logueado no tenga session_key si ya está asociado a un cliente
            if cart and cart.session_key:
                print(f"DEBUG _get_or_create_cart: Limpiando session_key del carrito {cart.id} del usuario.")
                cart.session_key = None
                cart.save()

        except Usuario.DoesNotExist:
            print(f"ADVERTENCIA _get_or_create_cart: usuario_id {request.session.get('usuario_id')} en sesión no encontrado. Tratando como anónimo.")
            for key in ['usuario_id', 'usuario_nombre', 'usuario_rol', 'previous_session_key_before_login']:
                if key in request.session:
                    del request.session[key]
            cliente_actual = None # Forzar tratamiento como anónimo

    if not cliente_actual: # Usuario anónimo
        print(f"DEBUG _get_or_create_cart: Usuario es anónimo. Session key: {session_key_actual}")
        cart, created = Carrito.objects.get_or_create(
            session_key=session_key_actual, 
            activo=True, #
            id_cliente__isnull=True, 
            defaults={'total': 0.00} #
        )
        if created:
            print(f"DEBUG _get_or_create_cart: Nuevo carrito de sesión creado: {cart.id}")
        else:
            print(f"DEBUG _get_or_create_cart: Carrito de sesión encontrado: {cart.id}")
    
    if cart: # Recalcular y guardar el total del carrito
        cart.total = cart.total_calculado #
        cart.save()
        print(f"DEBUG _get_or_create_cart: Total del carrito {cart.id} recalculado a: {cart.total}")
        
    return cart

def productos(request):
    lista_de_productos = Producto.objects.all() #
    cart = _get_or_create_cart(request)
    cart_items_count = 0
    if cart:
        result = CarritoItem.objects.filter(id_carrito=cart).aggregate(total_cantidad=Sum('cantidad')) #
        cart_items_count = result['total_cantidad'] if result['total_cantidad'] is not None else 0
        
    context = {
        'productos': lista_de_productos,
        'cart_items_count': cart_items_count
    }
    return render(request, 'web/index.html', context) # Ruta corregida

@require_POST
def agregar_al_carrito(request):
    product_id = request.POST.get('product_id')
    cantidad_a_anadir = int(request.POST.get('cantidad', 1))

    if not product_id:
        return JsonResponse({'success': False, 'error': 'ID de producto no proporcionado'}, status=400)

    producto_obj = get_object_or_404(Producto, id=product_id) #
    cart = _get_or_create_cart(request)

    cart_item, created = CarritoItem.objects.get_or_create(
        id_carrito=cart, #
        id_producto=producto_obj, #
        defaults={'cantidad': 0} #
    )

    cantidad_final_deseada = cart_item.cantidad + cantidad_a_anadir #

    if cantidad_final_deseada > producto_obj.stock: #
        return JsonResponse({
            'success': False, 
            'error': f'Stock insuficiente para {producto_obj.nombre}. Disponible: {producto_obj.stock}, en carrito: {cart_item.cantidad}' #
        }, status=400)
    
    cart_item.cantidad = cantidad_final_deseada #
    cart_item.save()
    
    message = f'{cantidad_a_anadir} x {producto_obj.nombre} añadido(s)/actualizado(s).' #

    items_en_carrito_qs = CarritoItem.objects.filter(id_carrito=cart) #
    total_items_in_cart = items_en_carrito_qs.aggregate(total_cantidad=Sum('cantidad'))['total_cantidad'] or 0
    
    cart.total = cart.total_calculado #
    cart.save()
    
    return JsonResponse({
        'success': True, 
        'message': message,
        'cart_total_items': total_items_in_cart
    })

def ver_carrito_api(request):
    cart = _get_or_create_cart(request)
    items_data = []
    cart_total_value_decimal = 0
    total_items_count = 0

    if cart:
        cart_items = CarritoItem.objects.filter(id_carrito=cart).select_related('id_producto') #
        for item in cart_items:
            items_data.append({
                'id': str(item.id), #
                'product_id': str(item.id_producto.id), #
                'nombre': item.id_producto.nombre, #
                'precio': float(item.id_producto.precio), #
                'cantidad': item.cantidad, #
                'subtotal': float(item.subtotal_calculado), 
                'imagen_url': None, 
                'stock_producto': item.id_producto.stock #
            })
        total_items_count = sum(i['cantidad'] for i in items_data)
        cart_total_value_decimal = cart.total_calculado #

    return JsonResponse({
        'items': items_data,
        'total_items_count': total_items_count,
        'cart_total_value': float(cart_total_value_decimal)
    })

@require_POST
def actualizar_cantidad_carrito(request):
    item_id = request.POST.get('item_id')
    nueva_cantidad = int(request.POST.get('cantidad', 0))
    
    cart_item = get_object_or_404(CarritoItem, id=item_id) #
    cart = _get_or_create_cart(request)

    if cart_item.id_carrito != cart: #
        return JsonResponse({'success': False, 'error': 'Acción no permitida'}, status=403)

    producto = cart_item.id_producto #
    
    if nueva_cantidad <= 0:
        cart_item.delete()
        message = f'{producto.nombre} eliminado del carrito.' #
    elif nueva_cantidad > producto.stock: #
        return JsonResponse({'success': False, 'error': f'Stock insuficiente. Disponible: {producto.stock}'}, status=400) #
    else:
        cart_item.cantidad = nueva_cantidad #
        cart_item.save()
        message = f'Cantidad de {producto.nombre} actualizada.' #

    items_en_carrito_qs = CarritoItem.objects.filter(id_carrito=cart) #
    total_items_in_cart = items_en_carrito_qs.aggregate(total_cantidad=Sum('cantidad'))['total_cantidad'] or 0
    cart.total = cart.total_calculado #
    cart.save()

    return JsonResponse({'success': True, 'message': message, 'cart_total_items': total_items_in_cart})

@require_POST
def eliminar_del_carrito(request):
    item_id = request.POST.get('item_id')
    cart_item = get_object_or_404(CarritoItem, id=item_id) #
    cart = _get_or_create_cart(request)

    if cart_item.id_carrito != cart: #
        return JsonResponse({'success': False, 'error': 'Acción no permitida'}, status=403)

    nombre_producto = cart_item.id_producto.nombre #
    cart_item.delete()

    items_en_carrito_qs = CarritoItem.objects.filter(id_carrito=cart) #
    total_items_in_cart = items_en_carrito_qs.aggregate(total_cantidad=Sum('cantidad'))['total_cantidad'] or 0
    cart.total = cart.total_calculado #
    cart.save()
    
    return JsonResponse({'success': True, 'message': f'{nombre_producto} eliminado.', 'cart_total_items': total_items_in_cart})

# Tus otras vistas originales, ahora apuntando a la subcarpeta 'web/'



def logout(request):
    request.session.flush()
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect('Ferremas:index')


def validar_rut(rut):
    """Valida el RUT chileno con formato 12345678-5"""
    rut = rut.replace(".", "").replace("-", "").upper()
    if not rut[:-1].isdigit() or len(rut) < 2:
        return False

    cuerpo = rut[:-1]
    verificador = rut[-1]

    suma = 0
    multiplo = 2

    for d in reversed(cuerpo):
        suma += int(d) * multiplo
        multiplo += 1
        if multiplo > 7:
            multiplo = 2

    resto = 11 - (suma % 11)
    if resto == 11:
        dv = '0'
    elif resto == 10:
        dv = 'K'
    else:
        dv = str(resto)

    return verificador == dv

def confirmar_correo(request):
    return render(request, 'web/confirmar_correo.html', {'usuario': True})

@rol_requerido(['Cliente'])
@never_cache 
def cuenta_cliente(request):
    email_sesion = request.session.get('user_email')  # debe ser el mismo key que usas en login
    access_token = request.session.get('access_token')
    refresh_token = request.session.get('refresh_token')

    if not email_sesion or not access_token or not refresh_token:
        messages.info(request, "Sesión expirada. Por favor Inicia sesion nuevamente.")
        return redirect('Ferremas:login')

    try:
        usuario = Usuario.objects.get(email=email_sesion)
    except Usuario.DoesNotExist:
        messages.info(request, "Usuario no encontrado.")
        return redirect('Ferremas:login')

    if request.method == 'POST' and request.POST.get('accion') == 'cambiar_contrasena':
        nueva_contrasena = request.POST.get('nueva_contrasena')
        confirmar_contrasena = request.POST.get('confirmar_contrasena')

        if not (nueva_contrasena and confirmar_contrasena):
            messages.info(request, 'Por favor. Debe completar ambos campos para cambiar contraseña')
        elif nueva_contrasena != confirmar_contrasena:
            messages.info(request, 'Las contraseñas no coinciden. Por favor verifica')
        else:
            # Validaciones de seguridad para la nueva contraseña
            if not any(c.isupper() for c in nueva_contrasena):
                messages.info(request, 'La contraseña debe contener al menos una letra mayúscula')
            elif not any(c.isdigit() for c in nueva_contrasena):
                messages.info(request, 'La contraseña debe contener al menos un número')
            elif len(nueva_contrasena) < 8:
                messages.info(request, 'La contraseña debe tener al menos 8 caracteres')
            else:
                try:
                    # Refrescar sesión para obtener tokens válidos
                    session_data = supabase.auth.refresh_session(refresh_token)
                    if not session_data.session:
                        messages.info(request, "No se pudo renovar la sesión. Por favor inicia sesión nuevamente.")
                        return redirect('Ferremas:login')

                    access_token = session_data.session.access_token
                    refresh_token = session_data.session.refresh_token
                    request.session['access_token'] = access_token
                    request.session['refresh_token'] = refresh_token

                    # Establecer la sesión actual en supabase
                    supabase.auth.set_session(access_token, refresh_token)

                    # Cambiar la contraseña
                    response = supabase.auth.update_user({"password": nueva_contrasena})

                    print("Supabase update_user response:", response)

                    if response.user:

                        try:
                            login_response = supabase.auth.sign_in_with_password({
                                'email': email_sesion,
                                'password': nueva_contrasena
                            })

                            print("Intento login con nueva contraseña:", login_response)

                            if login_response.user and login_response.session:
                                messages.success(request, 'Contraseña actualizada correctamente. Por favor, inicia sesión con tu nueva contraseña.')
                            else:
                                messages.info(request, 'No se pudo iniciar sesión con la nueva contraseña. Intenta nuevamente.')

                        except Exception as e_login:
                            messages.info(request, f'Error iniciando sesión tras cambio: {str(e_login)}')

                        # Cerrar sesión para forzar re-login
                        for key in ['user_email', 'supabase_uid', 'access_token', 'refresh_token', 'usuario_id', 'usuario_nombre', 'usuario_rol']:
                            if key in request.session:
                                del request.session[key]
                        return redirect('Ferremas:login')
                    else:
                        messages.info(request, 'No se pudo actualizar la contraseña en Supabase.')
                except Exception as e:
                    messages.info(request, f'Error al cambiar contraseña: {str(e)}')

        return redirect('Ferremas:cuenta_cliente')

    context = {
        'usuario': usuario,
    }
    return render(request, 'web/cuenta_cliente.html', context)

def comprar(request):
    if 'usuario_id' not in request.session:
        return redirect('Ferremas:login')

    print("DEBUG comprar: Vista 'comprar' iniciada.")
    cart = _get_or_create_cart(request)

    if not cart:
        messages.error(request, "No se pudo obtener o crear un carrito.")
        print("ERROR comprar: _get_or_create_cart devolvió None.")
        return redirect('Ferremas:productos')

    print(f"DEBUG comprar: Carrito ID: {cart.id}, Cliente ID del Carrito: {cart.id_cliente}, Session Key del Carrito: {cart.session_key}")

    # Asegura que el carrito esté vinculado al usuario logueado
    if not cart.id_cliente:
        if 'usuario_id' in request.session:
            try:
                cliente_actual = Usuario.objects.get(id=request.session['usuario_id'])
                cart.id_cliente = cliente_actual
                cart.session_key = None # Limpia la session_key al asociar al usuario
                cart.save()
                print(f"DEBUG comprar: Carrito {cart.id} asociado forzosamente al cliente {cliente_actual.id}.")
            except Usuario.DoesNotExist:
                print(f"ERROR comprar: usuario_id {request.session['usuario_id']} inválido.")
                return redirect('Ferremas:login')
        else:
            print("ERROR comprar: request.user autenticado pero no hay 'usuario_id' en sesión.")
            return redirect('Ferremas:login')

    cliente_para_pedido = cart.id_cliente
    if not cliente_para_pedido:
        messages.error(request, "No se pudo identificar al cliente.")
        return redirect('Ferremas:login')

    cart_items_list = CarritoItem.objects.filter(id_carrito=cart).select_related('id_producto')

    if not cart_items_list and request.method == 'GET':
        messages.info(request, "Tu carrito está vacío.")
        return redirect('Ferremas:productos')

    if request.method == 'POST':
        try:
            print("DEBUG comprar (POST): Inicio de creación de pedido.")
            costo_envio_str = request.POST.get('costo_envio', '0')
            try:
                costo_envio = Decimal(costo_envio_str) # Asegúrate que sea Decimal
            except (ValueError, InvalidOperation):
                costo_envio = Decimal('0.00')

            total_productos_calculado = cart.total_calculado
            total_final_pedido = total_productos_calculado + costo_envio

            with transaction.atomic():  # Asegura rollback si algo falla
                nuevo_pedido = Pedido.objects.create(
                    id_cliente=cliente_para_pedido,
                    estado='Pendiente',
                    id_carrito=cart,
                    total_pedido=total_final_pedido,
                    fecha=timezone.now().date()
                )
                print(f"DEBUG: Pedido creado: {nuevo_pedido.id}")

                for item_carrito in cart_items_list:
                    DetallePedido.objects.create(
                        id_pedido=nuevo_pedido,
                        id_producto=item_carrito.id_producto,
                        cantidad=item_carrito.cantidad,
                        subtotal=item_carrito.subtotal_calculado
                    )
                    print(f"DEBUG: DetallePedido creado para producto {item_carrito.id_producto.nombre}")

                cart.activo = False
                cart.save()
                print(f"DEBUG: Carrito {cart.id} marcado como inactivo.")

                request.session['pedido_id_para_pago'] = str(nuevo_pedido.id)
                if 'previous_session_key_before_login' in request.session:
                    del request.session['previous_session_key_before_login']

                # REDIRECCIÓN A LA SIMULACIÓN INTERNA
                return redirect('Ferremas:simular_pago_transbank')

        except Exception as e:
            import traceback
            traceback.print_exc()
            messages.error(request, f"Ocurrió un error al procesar tu compra: {str(e)}")
            return redirect('Ferremas:productos')

    context = {
        'carrito': cart,
        'cart_items': cart_items_list,
        'usuario_actual': cliente_para_pedido
    }
    return render(request, 'web/comprar.html', context)


# VISTA PARA LA SIMULACIÓN INTERNA DE PAGO
def simular_pago_transbank(request): # Mantenemos este nombre como estaba originalmente
    pedido_id = request.session.get('pedido_id_para_pago')

    if not pedido_id:
        return redirect('Ferremas:productos')

    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        pago_exitoso = request.POST.get('pago_exitoso') == 'true'
        metodo_pago_obj, _ = MetodoPago.objects.get_or_create(tipo_pago='Transbank Webpay (Simulado)')

        if pago_exitoso:
            pedido.estado = 'Pagado'
            Pago.objects.create(
                id_pedido=pedido,
                metodo=metodo_pago_obj,
                monto=pedido.total_pedido,
                estado=EstadoPago.PAGADO
            )
            # Descontar el stock de los productos del pedido (¡DESCOMENTA ESTO!)
            for detalle in pedido.detallepedido_set.all():
                producto_pedido = detalle.id_producto
                if producto_pedido.stock >= detalle.cantidad:
                    producto_pedido.stock -= detalle.cantidad
                    producto_pedido.save()
                else:
                    print(f"ERROR CRÍTICO DE STOCK para producto {producto_pedido.id} en pedido {pedido.id}. Esto no debería suceder si se validó antes.")
            pedido.save()
            if 'pedido_id_para_pago' in request.session:
                del request.session['pedido_id_para_pago']
            return render(request, 'web/pago_exitoso.html', {'pedido': pedido})
        else:
            pedido.estado = 'Pago Rechazado'
            Pago.objects.create(
                id_pedido=pedido,
                metodo=metodo_pago_obj,
                monto=pedido.total_pedido,
                estado=EstadoPago.RECHAZADO
            )
            pedido.save()
            # No borramos pedido_id_para_pago de la sesión para que pueda reintentar
            return render(request, 'web/pago_fallido.html', {'pedido': pedido})

    context = {
        'pedido': pedido,
        'monto_a_pagar': pedido.total_pedido,
    }
    return render(request, 'web/simulacion_pago.html', context)

@rol_requerido(['Vendedor'])
def vendedor(request):
    return render(request, 'web/vendedor.html')

@rol_requerido(['Vendedor'])
def gestion_pedidos(request):
    pedidos = Pedido.objects.select_related('id_cliente').all()

    # === Filtros ===
    estado = request.GET.get('estado')
    fecha_filtro = request.GET.get('fecha')
    search_query = request.GET.get('busqueda')

    if estado and estado != 'Todos':
        pedidos = pedidos.filter(estado=estado)

    if fecha_filtro:
        hoy = date.today()
        if fecha_filtro == 'Hoy':
            pedidos = pedidos.filter(fecha=hoy)
        elif fecha_filtro == 'Ayer':
            pedidos = pedidos.filter(fecha=hoy - timedelta(days=1))
        elif fecha_filtro == 'Esta semana':
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            pedidos = pedidos.filter(fecha__range=(inicio_semana, hoy))

    if search_query:
        pedidos = pedidos.filter(
            Q(id__icontains=search_query) |
            Q(id_cliente__nombre__icontains=search_query) |
            Q(id_cliente__apellido__icontains=search_query)
        )

    context = {
        'pedidos': pedidos
    }
    return render(request, 'web/gestion_pedidos.html', context)

@rol_requerido(['Vendedor'])
def productos_bodega(request):
    productos = Producto.objects.select_related('id_tipo_producto')

    # === Filtros ===
    busqueda = request.GET.get('q')
    categoria = request.GET.get('categoria')
    solo_bajo_stock = request.GET.get('bajo_stock') == '1'

    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) |
            Q(id__icontains=busqueda)
        )

    if categoria and categoria != 'todas':
        productos = productos.filter(id_tipo_producto__nombre__iexact=categoria)

    if solo_bajo_stock:
        productos = productos.filter(stock__lt=10)  # umbral configurable

    context = {
        'productos': productos,
        'q': busqueda,
        'categoria': categoria,
        'bajo_stock': solo_bajo_stock,
    }
    return render(request, 'web/productos_bodega.html', context)

@rol_requerido(['Vendedor'])
def ordenes_despacho(request):
    ordenes = Pedido.objects.select_related('id_cliente').all()

    # Filtros
    estado = request.GET.get('estado')
    metodo_entrega = request.GET.get('entrega')
    busqueda = request.GET.get('busqueda')

    if estado and estado != 'Todos':
        ordenes = ordenes.filter(estado_despacho=estado)

    if metodo_entrega and metodo_entrega != 'Todos':
        ordenes = ordenes.filter(metodo_entrega=metodo_entrega)

    if busqueda:
        ordenes = ordenes.filter(
            Q(id__icontains=busqueda) |
            Q(id_cliente__nombre__icontains=busqueda) |
            Q(id_cliente__apellido__icontains=busqueda)
        )

    contexto = {
        'ordenes': ordenes
    }
    return render(request, 'web/ordenes_despacho.html', contexto)

@require_POST
def marcar_enviado(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.estado_despacho = 'Enviado'
    pedido.save()

    # Crear registro en Entrega si no existe aún
    Entrega.objects.get_or_create(pedido=pedido)

    return redirect('Ferremas:ordenes_despacho')

@rol_requerido(['Bodeguero'])
def bodeguero(request):
    return render(request,'web/bodeguero.html')

@rol_requerido(['Bodeguero'])
def ordenes_pedido(request):
    pedidos = Pedido.objects.select_related('id_cliente').prefetch_related('detallepedido_set', 'detallepedido_set__id_producto')

    estado = request.GET.get('estado')
    fecha_filtro = request.GET.get('fecha')
    busqueda = request.GET.get('busqueda')

    if estado and estado != 'Todos':
        pedidos = pedidos.filter(estado=estado)

    if fecha_filtro:
        hoy = date.today()
        if fecha_filtro == 'Hoy':
            pedidos = pedidos.filter(fecha=hoy)
        elif fecha_filtro == 'Últimos 7 días':
            pedidos = pedidos.filter(fecha__gte=hoy - timedelta(days=7))

    if busqueda:
        pedidos = pedidos.filter(
            Q(id_cliente__nombre__icontains=busqueda) |
            Q(id_cliente__apellido__icontains=busqueda)
        )

    pedidos_datos = []
    for pedido in pedidos:
        productos = ", ".join([f"{dp.id_producto.nombre} (x{dp.cantidad})" for dp in pedido.detallepedido_set.all()])
        pedidos_datos.append({
            'id': pedido.id,
            'numero': str(pedido.id)[:8],
            'cliente': f"{pedido.id_cliente.nombre} {pedido.id_cliente.apellido}",
            'producto': productos,
            'fecha': pedido.fecha,
            'estado': pedido.estado,
        })

    context = {'pedidos': pedidos_datos}
    return render(request, 'web/ordenes_pedido.html', context)

@require_POST
def preparar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.estado = 'Preparado'
    pedido.save()
    return redirect('Ferremas:ordenes_pedido')

@require_POST
def entregar_a_vendedor(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.estado = 'Entregado'
    pedido.save()
    return redirect('Ferremas:ordenes_pedido')


@rol_requerido(['Contador'])
def contador(request):
    return render(request,'web/contador.html')

from django.views.decorators.http import require_http_methods

@rol_requerido(['Contador'])
def confirmar_pagos(request):
    pagos = Pago.objects.select_related('id_pedido__id_cliente', 'metodo').all()

    cliente = request.GET.get('cliente')
    metodo = request.GET.get('metodo')
    estado = request.GET.get('estado')

    if cliente:
        pagos = pagos.filter(
            Q(id_pedido__id_cliente__nombre__icontains=cliente) |
            Q(id_pedido__id_cliente__apellido__icontains=cliente)
        )

    if metodo:
        pagos = pagos.filter(metodo_id=metodo)

    if estado:
        pagos = pagos.filter(estado=estado)

    metodos_pago = MetodoPago.objects.all()

    return render(request, 'web/confirmar_pagos.html', {
        'pagos': pagos,
        'metodos_pago': metodos_pago
    })

@require_POST
@rol_requerido(['Contador'])
def confirmar_pago(request, pk):
    pago = get_object_or_404(Pago, id=pk)
    pago.estado = EstadoPago.PAGADO
    pago.save()
    messages.success(request, "Pago confirmado correctamente.")
    return redirect('Ferremas:confirmar_pagos')

@rol_requerido(['Contador'])
def registrar_entregas(request):
    entregas = Entrega.objects.select_related('pedido__id_cliente').all()

    # Filtros
    fecha_filtro = request.GET.get('fecha')
    estado_filtro = request.GET.get('estado')
    cliente_q = request.GET.get('cliente')

    if fecha_filtro == 'Hoy':
        entregas = entregas.filter(fecha=date.today())
    elif fecha_filtro == 'Últimos 7 días':
        entregas = entregas.filter(fecha__gte=date.today() - timedelta(days=7))

    if estado_filtro and estado_filtro != 'Todos':
        entregas = entregas.filter(estado=estado_filtro)

    if cliente_q:
        entregas = entregas.filter(
            Q(pedido__id_cliente__nombre__icontains=cliente_q) |
            Q(pedido__id_cliente__apellido__icontains=cliente_q)
        )

    context = {
        'entregas': [
            {
                'id': entrega.id,
                'cliente': f"{entrega.pedido.id_cliente.nombre} {entrega.pedido.id_cliente.apellido}",
                'numero_pedido': entrega.pedido.id,
                'fecha': entrega.fecha,
                'estado': entrega.estado
            }
            for entrega in entregas
        ]
    }
    return render(request, 'web/registrar_entregas.html', context)

#Vista para registrar la entrega
@require_POST
@rol_requerido(['Contador'])
def confirmar_entrega(request, entrega_id):
    entrega = get_object_or_404(Entrega, id=entrega_id)
    entrega.estado = 'Registrado'
    entrega.save()
    return redirect('Ferremas:registrar_entregas')

@rol_requerido(['Administrador'])
def administrador(request):
    return render(request,'web/administrador.html')

@rol_requerido(['Administrador'])
def informe_venta_mensual(request):
    anos = range(2024, 2027)
    año_actual = 2025

    if request.method == 'POST':
        mes = int(request.POST.get('mes'))
        año = int(request.POST.get('año'))

        pedidos_filtrados = Pedido.objects.filter(fecha__year=año, fecha__month=mes)
        resumen = pedidos_filtrados.aggregate(
            total_ventas=Sum('total_pedido'),
            total_pedidos=Count('id')
        )

        nombre_mes = calendar.month_name[mes]

        data = {
            'mes': nombre_mes,
            'año': año,
            'total_ventas': float(resumen['total_ventas'] or 0),
            'total_pedidos': resumen['total_pedidos']
        }

        return JsonResponse({'success': True, 'data': data})

    return render(request, 'web/informe_venta_mensual.html', {
        'años': anos,
        'año_actual': año_actual
    })

@rol_requerido(['Administrador'])
def informe_desempeno(request):
    return render(request,'web/informe_desempeno.html')

@rol_requerido(['Administrador'])
def datos_informe_desempeno(request):
    sucursal = request.GET.get('sucursal', None)
    periodo = request.GET.get('periodo', 'Ultimos 30 Dias')

    hoy = date.today()
    if periodo == "Este Mes":
        inicio = hoy.replace(day=1)
    elif periodo == "Ultimos 3 Meses":
        inicio = hoy - timedelta(days=90)
    else:
        inicio = hoy - timedelta(days=30)

    pedidos = Pedido.objects.filter(fecha__gte=inicio)

    if sucursal and sucursal != "Todas":
        pedidos = pedidos.filter(id_cliente__direccion__id_region__nombre=sucursal)

    total = pedidos.count()
    completados = pedidos.filter(estado="Pagado").count()

    # Tiempo promedio real de entrega
    entregas = Entrega.objects.filter(pedido__in=pedidos, fecha_entrega__isnull=False)
    entregas = entregas.annotate(
        duracion=ExpressionWrapper(
            F('fecha_entrega') - F('pedido__fecha'),
            output_field=DurationField()
        )
    )
    promedio_dias = entregas.aggregate(promedio=Avg('duracion'))['promedio']
    tiempo_entrega_prom = f"{promedio_dias.days} días" if promedio_dias else "Sin datos"

    # Nivel de satisfacción si tienes tabla de encuestas
    from Ferremas.models import EncuestaSatisfaccion
    encuestas = EncuestaSatisfaccion.objects.filter(pedido__in=pedidos)
    promedio_satisfaccion = encuestas.aggregate(promedio=Avg('puntaje'))['promedio']
    satisfaccion = f"{round(promedio_satisfaccion * 20)}%" if promedio_satisfaccion else "Sin datos"

    return JsonResponse({
        "satisfaccion": satisfaccion,
        "tiempo_entrega": tiempo_entrega_prom,
        "completados": f"{completados} / {total}"
    })

@rol_requerido(['Administrador'])
def ventas_promociones(request):
    return render(request,'web/ventas_promociones.html')

@rol_requerido(['Administrador'])
def crear_promocion(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descuento = request.POST.get('descuento')
        desde = request.POST.get('desde')
        hasta = request.POST.get('hasta')

        # Validaciones básicas
        if not nombre or not descuento or not desde or not hasta:
            messages.error(request, "Completa todos los campos obligatorios.")
            return redirect('Ferremas:crear_promocion')

        if int(descuento) < 1 or int(descuento) > 100:
            messages.error(request, "El descuento debe estar entre 1% y 100%.")
            return redirect('Ferremas:crear_promocion')

        # Crear promoción
        Promocion.objects.create(
            nombre=nombre,
            descuento=descuento,
            fecha_inicio=desde,
            fecha_fin=hasta
        )
        messages.success(request, "Promoción creada con éxito.")
        return redirect('Ferremas:promociones_activas')

    return render(request, 'web/crear_promocion.html')

@rol_requerido(['Administrador'])
def promociones_activas(request):
    hoy = date.today()
    promociones = Promocion.objects.filter(activo=True, fecha_inicio__lte=hoy, fecha_fin__gte=hoy)
    return render(request, 'web/promociones_activas.html', {
        'promociones': promociones
    })

@rol_requerido(['Administrador'])
@require_POST
def eliminar_promocion(request, promo_id):
    promocion = get_object_or_404(Promocion, id=promo_id)
    promocion.delete()
    return redirect('Ferremas:promociones_activas')

@rol_requerido(['Administrador'])
def editar_promocion(request, promo_id):
    promocion = get_object_or_404(Promocion, id=promo_id)

    if request.method == 'POST':
        promocion.nombre = request.POST['nombre']
        promocion.descuento = request.POST['descuento']
        promocion.fecha_inicio = request.POST['desde']
        promocion.fecha_fin = request.POST['hasta']
        promocion.save()
        return redirect('Ferremas:promociones_activas')

    return render(request, 'web/editar_promocion.html', {'promocion': promocion})

@rol_requerido(['Administrador'])
def gestion_usuarios(request):
    return render(request,'web/gestion_usuarios.html')

@rol_requerido(['Administrador'])
def crear_usuario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        rol = request.POST.get('rol')
        rut = request.POST.get('rut')

        if not all([nombre, correo, contrasena, rol, rut]):
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect('Ferremas:crear_usuario')

        partes = nombre.strip().split()
        if len(partes) < 2:
            messages.error(request, "Ingresa nombre y apellido.")
            return redirect('Ferremas:crear_usuario')

        nombre_real = " ".join(partes[:-1])
        apellido_real = partes[-1]

        try:
            auth_response = supabase.auth.sign_up({
                'email': correo,
                'password': contrasena
            })
            if not auth_response.user:
                messages.error(request, "No se pudo crear el usuario en Supabase.")
                return redirect('Ferremas:crear_usuario')
        except Exception as e:
            messages.error(request, f"Error al crear cuenta: {str(e)}")
            return redirect('Ferremas:crear_usuario')

        tipo_usuario, _ = TipoUsuario.objects.get_or_create(tipo_rol=rol.capitalize())
        Usuario.objects.create(
            nombre=nombre_real,
            apellido=apellido_real,
            email=correo,
            rut=rut,
            id_tipo_usuario=tipo_usuario
        )

        messages.success(request, "Usuario creado correctamente.")
        return redirect('Ferremas:usuarios_existentes')

    return render(request, 'web/crear_usuario.html')






