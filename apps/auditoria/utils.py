from .models import LogAuditoria
from .middleware import get_current_user, get_current_ip

def registrar_log(accion, tabla_afectada, registro_id=None, detalles="", usuario=None, ip_origen=None):
    """
    Función utilitaria para registrar un evento de auditoría de forma consistente.
    Utiliza el contexto del middleware si el usuario o la IP no se proporcionan explícitamente.
    """
    user = usuario or get_current_user()
    ip = ip_origen or get_current_ip()
    
    return LogAuditoria.objects.create(
        usuario=user if (user and user.is_authenticated) else None,
        accion=accion,
        tabla_afectada=tabla_afectada,
        registro_id=str(registro_id) if registro_id is not None else None,
        detalles=detalles,
        ip_origen=ip or '127.0.0.1'
    )
