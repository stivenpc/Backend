from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class PerfilUsuario(models.Model):
    ROLES = (
        ('OPERADOR', 'Operador de Planta'),
        ('SUPERVISOR', 'Supervisor de Turno'),
        ('ENCARGADO', 'Encargado / Jefe de Planta'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil', verbose_name="Usuario")
    rol = models.CharField(max_length=20, choices=ROLES, default='OPERADOR', verbose_name="Rol en Planta")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    area = models.CharField(max_length=100, default='Fundición y Moldeo', verbose_name="Área Asignada")

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - Rol: {self.get_rol_display()}"

    @property
    def es_operador(self):
        return self.rol == 'OPERADOR'

    @property
    def es_supervisor(self):
        return self.rol == 'SUPERVISOR' or self.user.is_superuser

    @property
    def es_encargado(self):
        return self.rol == 'ENCARGADO' or self.user.is_superuser

@receiver(post_save, sender=User)
def asegurar_perfil_usuario(sender, instance, created, **kwargs):
    """Garantiza que todo usuario creado disponga de un PerfilUsuario con su rol."""
    if created:
        PerfilUsuario.objects.get_or_create(user=instance, defaults={'rol': 'ENCARGADO' if instance.is_superuser else 'OPERADOR'})
    else:
        if not hasattr(instance, 'perfil'):
            PerfilUsuario.objects.create(user=instance, rol='ENCARGADO' if instance.is_superuser else 'OPERADOR')
