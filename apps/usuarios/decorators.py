from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def rol_requerido(*roles_permitidos):
    """
    Decorador para restringir el acceso a vistas según el rol de PerfilUsuario.
    Los superusuarios siempre tienen acceso concedido.
    """
    def decorador(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Debe iniciar sesión para acceder a esta sección.")
                return redirect('usuarios:login')

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            perfil = getattr(request.user, 'perfil', None)
            if not perfil or perfil.rol not in roles_permitidos:
                roles_str = ", ".join(roles_permitidos)
                messages.error(
                    request,
                    f"Acceso Denegado: Su rol actual ({perfil.get_rol_display() if perfil else 'Sin Rol'}) "
                    f"no tiene autorización para esta operación. Se requiere perfil: {roles_str}."
                )
                return redirect('operaciones:dashboard')

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorador

def supervisor_o_encargado_requerido(view_func):
    return rol_requerido('SUPERVISOR', 'ENCARGADO')(view_func)

def encargado_requerido(view_func):
    return rol_requerido('ENCARGADO')(view_func)
