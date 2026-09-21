from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .utils import registrar_log
from .middleware import get_current_ip

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ip = get_current_ip()
    registrar_log(
        accion='LOGIN',
        tabla_afectada='auth_user',
        registro_id=user.id,
        detalles=f"Inicio de sesión exitoso del usuario: {user.username} ({user.get_full_name() or 'Sin nombre'})",
        usuario=user,
        ip_origen=ip
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user:
        ip = get_current_ip()
        registrar_log(
            accion='LOGOUT',
            tabla_afectada='auth_user',
            registro_id=user.id,
            detalles=f"Cierre de sesión del usuario: {user.username}",
            usuario=user,
            ip_origen=ip
        )

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    username = credentials.get('username', 'Desconocido')
    ip = get_current_ip()
    registrar_log(
        accion='LOGIN',
        tabla_afectada='auth_user',
        registro_id=None,
        detalles=f"Intento fallido de inicio de sesión con el nombre de usuario: {username}",
        usuario=None,
        ip_origen=ip
    )
