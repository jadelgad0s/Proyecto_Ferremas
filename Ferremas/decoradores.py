from django.shortcuts import redirect
from functools import wraps

def rol_requerido(roles_permitidos):
    def decorador(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            rol = request.session.get('usuario_rol')

            if rol in roles_permitidos:
                return view_func(request, *args, **kwargs)
            else:
                # Redirige a donde tú quieras (por ejemplo al index)
                return redirect('Ferremas:index')
        return _wrapped_view
    return decorador
