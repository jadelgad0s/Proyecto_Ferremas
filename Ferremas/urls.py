# Ferremas/urls.py
from django.urls import path
from .views import * # Importa todas las funciones de views.py
from django.conf import settings
from django.conf.urls.static import static

app_name = 'Ferremas'

urlpatterns = [
    path('', index, name='index'),
    path('index/', index, name='index'),
    #api
    #path('eliminar_usuario/<uuid:id>/', eliminar_usuario, name='eliminar_usuario'),
    path('editar_usuario/<uuid:id>/', editar_usuario, name='editar_usuario'),
    path('api/usuarios/<uuid:id>/editar/eliminar/', EditarEliminarUsuarioApiView.as_view(), name='api-editar-eliminar-usuario'), #api
    path('usuarios_existentes/', usuarios_existentes, name='usuarios_existentes'),
    path('api/usuarios_existentes/', UsuariosExistentesApiView.as_view(), name='api-usuarios-existentes'), #api con JSON
    path('login/', pagina_login, name='vista_login'), 
    path('api/login/', LoginApiView.as_view(), name='api-login'),  # api con JSON
    path('registro/', pagina_registro, name='vista_registro'),
    path('api/registro/', RegistroApiView.as_view(), name='api-registro'),#api con JSON
    path('logout/', logout, name='logout'),
    path('cuenta_cliente/', cuenta_cliente, name='cuenta_cliente'),
    path('comprar/', comprar, name='comprar'),
    path('productos/', productos, name='productos'),
    path('vendedor/', vendedor, name='vendedor'),
    path('gestion_pedidos/', gestion_pedidos, name='gestion_pedidos'),
    path('productos_bodega/', productos_bodega, name='productos_bodega'),
    path('ordenes_despacho/', ordenes_despacho, name='ordenes_despacho'),
    path('bodeguero/', bodeguero, name='bodeguero'),
    path('ordenes_pedido/', ordenes_pedido, name='ordenes_pedido'),
    path('contador/', contador, name='contador'),
    path('confirmar_pagos/', confirmar_pagos, name='confirmar_pagos'),
    path('registrar_entregas/', registrar_entregas, name='registrar_entregas'),
    path('registrar_entrega/<uuid:entrega_id>/', confirmar_entrega, name='registrar_entrega'),
    path('administrador/', administrador, name='administrador'),
    path('informe_venta_mensual/', informe_venta_mensual, name='informe_venta_mensual'),
    path('informe_desempeno/', informe_desempeno, name='informe_desempeno'),
    path('ventas_promociones/', ventas_promociones, name='ventas_promociones'),
    path('crear_promocion/', crear_promocion, name='crear_promocion'),
    path('promociones_activas/', promociones_activas, name='promociones_activas'),
    path('eliminar_promocion/<uuid:promo_id>/', eliminar_promocion, name='eliminar_promocion'),
    path('editar_promocion/<uuid:promo_id>/', editar_promocion, name='editar_promocion'),
    path('gestion_usuarios/', gestion_usuarios, name='gestion_usuarios'),
    path('crear_usuario/', crear_usuario, name='crear_usuario'),
    path('confirmar_correo/', confirmar_correo, name='confirmar_correo'),
    path('ordenes_despacho/enviar/<uuid:pedido_id>/', marcar_enviado, name='marcar_enviado'),
    path('confirmar_pago/<uuid:pk>/', confirmar_pago, name='confirmar_pago'),
    path('ordenes_pedido/preparar/<uuid:pedido_id>/', preparar_pedido, name='preparar_pedido'),
    path('ordenes_pedido/entregar/<uuid:pedido_id>/', entregar_a_vendedor, name='entregar_a_vendedor'),
    path('api/informe_desempeno/', datos_informe_desempeno, name='api_informe_desempeno'),

    # URLs para la API del carrito
    path('carrito/agregar/', agregar_al_carrito, name='agregar_al_carrito_api'),
    path('carrito/ver/', ver_carrito_api, name='ver_carrito_api'),
    path('carrito/actualizar/', actualizar_cantidad_carrito, name='actualizar_cantidad_carrito_api'),
    path('carrito/eliminar/', eliminar_del_carrito, name='eliminar_del_carrito_api'),
    path('simulacion_pago/', simular_pago_transbank, name='simular_pago_transbank'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)