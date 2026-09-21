from django.contrib import admin
from .models import LogAuditoria

@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('fecha_hora', 'usuario', 'accion', 'tabla_afectada', 'registro_id', 'ip_origen')
    list_filter = ('accion', 'tabla_afectada', 'fecha_hora')
    search_fields = ('usuario__username', 'tabla_afectada', 'detalles', 'ip_origen', 'registro_id')
    readonly_fields = ('fecha_hora', 'usuario', 'accion', 'tabla_afectada', 'registro_id', 'detalles', 'ip_origen')
    ordering = ('-fecha_hora',)

    def has_add_permission(self, request):
        # Los logs de auditoría no pueden crearse manualmente desde el panel
        return False

    def has_change_permission(self, request, obj=None):
        # Los logs de auditoría son inmutables
        return False

    def has_delete_permission(self, request, obj=None):
        # Los logs de auditoría no pueden eliminarse (principio de no repudio)
        return False
