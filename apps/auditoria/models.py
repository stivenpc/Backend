from django.db import models
from django.contrib.auth.models import User

class LogAuditoria(models.Model):
    ACCIONES = (
        ('CREATE', 'Creación'),
        ('UPDATE', 'Modificación'),
        ('DELETE', 'Eliminación'),
        ('APROBAR', 'Aprobación Técnica'),
        ('LOGIN', 'Inicio de Sesión'),
        ('LOGOUT', 'Cierre de Sesión'),
    )

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuario")
    accion = models.CharField(max_length=15, choices=ACCIONES, verbose_name="Acción")
    tabla_afectada = models.CharField(max_length=60, verbose_name="Entidad / Tabla")
    registro_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="ID Registro")
    detalles = models.TextField(verbose_name="Detalle de la Operación")
    ip_origen = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP de Origen")
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")

    class Meta:
        verbose_name = "Log de Auditoría"
        verbose_name_plural = "Logs de Auditoría"
        ordering = ['-fecha_hora']

    def __str__(self):
        usr = self.usuario.username if self.usuario else "Sistema/Anónimo"
        return f"[{self.fecha_hora.strftime('%d/%m/%Y %H:%M:%S')}] {usr} - {self.accion} en {self.tabla_afectada}"
