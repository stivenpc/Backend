from django.urls import path
from . import views

app_name = 'operaciones'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),

    # Lotes de Materiales (M1)
    path('lotes/', views.lote_list, name='lote_list'),
    path('lotes/nuevo/', views.lote_create, name='lote_create'),
    path('lotes/<int:pk>/', views.lote_detail, name='lote_detail'),
    path('lotes/<int:pk>/editar/', views.lote_update, name='lote_update'),
    path('lotes/<int:pk>/eliminar/', views.lote_delete, name='lote_delete'),

    # Estudios Previos Obligatorios (M5)
    path('estudios/', views.estudio_list, name='estudio_list'),
    path('estudios/nuevo/', views.estudio_create, name='estudio_create'),
    path('estudios/<int:pk>/', views.estudio_detail, name='estudio_detail'),
    path('estudios/<int:pk>/aprobar/', views.estudio_aprobar, name='estudio_aprobar'),

    # Mermas Específicas (M4)
    path('mermas/', views.merma_list, name='merma_list'),
    path('mermas/nueva/', views.merma_create, name='merma_create'),
    path('mermas/<int:pk>/', views.merma_detail, name='merma_detail'),
    path('mermas/<int:pk>/editar/', views.merma_update, name='merma_update'),
    path('mermas/<int:pk>/eliminar/', views.merma_delete, name='merma_delete'),

    # Auditoría (M3)
    path('auditoria/', views.auditoria_list, name='auditoria_list'),
]
