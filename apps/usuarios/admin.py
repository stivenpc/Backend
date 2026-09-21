from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import PerfilUsuario

class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil de Planta y Rol (RBAC)'

class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'obtener_rol', 'is_staff', 'is_active')
    list_filter = ('perfil__rol', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'perfil__area')

    def obtener_rol(self, instance):
        if hasattr(instance, 'perfil'):
            return instance.perfil.get_rol_display()
        return "Sin perfil"
    obtener_rol.short_description = "Rol Asignado"

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(PerfilUsuario)
