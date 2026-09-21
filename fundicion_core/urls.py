"""
URL Configuration for fundicion_core project.
"""
from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "SIGMA - Sistema de Control de Mermas de Fundición"
admin.site.site_title = "Panel de Control SIGMA"
admin.site.index_title = "Administración de Fundición y Metalurgia"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('apps.usuarios.urls', namespace='usuarios')),
    path('', include('apps.operaciones.urls', namespace='operaciones')),
]
