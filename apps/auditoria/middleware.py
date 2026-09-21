import threading

_thread_locals = threading.local()

def get_current_user():
    return getattr(_thread_locals, 'user', None)

def get_current_ip():
    return getattr(_thread_locals, 'ip', None)

class AuditoriaMiddleware:
    """
    Middleware que captura el usuario autenticado y la IP de origen en almacenamiento local
    de hilo (thread-local) para enriquecer automáticamente las pistas de auditoría en señales y vistas.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.user = getattr(request, 'user', None) if request.user.is_authenticated else None
        
        # Captura de IP considerando proxies reversos
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        _thread_locals.ip = ip

        response = self.get_response(request)
        return response
