from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Material, LoteMaterial, EstudioPrevio, Maquina, Proceso, RegistroMerma

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'densidad_g_cm3', 'punto_fusion_c')
    search_fields = ('codigo', 'nombre', 'descripcion')
    list_per_page = 20


class RegistroMermaInline(admin.TabularInline):
    model = RegistroMerma
    extra = 0
    readonly_fields = ('fecha_registro', 'operador')
    fields = ('proceso', 'maquina', 'peso_merma_kg', 'tipo_merma', 'operador', 'fecha_registro')


@admin.register(LoteMaterial)
class LoteMaterialAdmin(admin.ModelAdmin):
    list_display = (
        'codigo_lote', 'material', 'peso_inicial_kg', 'peso_restante_badge',
        'porcentaje_merma_badge', 'fecha_ingreso', 'estado_estudio_badge'
    )
    list_filter = ('material', 'fecha_ingreso')
    search_fields = ('codigo_lote', 'material__nombre', 'proveedor', 'observaciones')
    readonly_fields = ('peso_restante_display', 'porcentaje_merma_display', 'total_merma_display')
    inlines = [RegistroMermaInline]

    fieldsets = (
        ('Identificación del Lote', {
            'fields': ('codigo_lote', 'material', 'proveedor', 'fecha_ingreso')
        }),
        ('Control de Balances e Inventario (M1)', {
            'fields': ('peso_inicial_kg', 'total_merma_display', 'peso_restante_display', 'porcentaje_merma_display')
        }),
        ('Observaciones Adicionales', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
    )

    def peso_restante_badge(self, obj):
        saldo = obj.peso_restante_kg
        color = "success" if saldo > 50 else "warning" if saldo > 0 else "danger"
        return format_html('<span class="badge bg-{}" style="font-weight:bold; color:{}">{} kg</span>',
                           color, "#2e7d32" if color=="success" else "#c62828", saldo)
    peso_restante_badge.short_description = "Saldo Restante"

    def porcentaje_merma_badge(self, obj):
        pct = obj.porcentaje_merma_actual
        color = "#2e7d32" if pct < 8 else "#e65100" if pct < 15 else "#c62828"
        return format_html('<span style="color:{}; font-weight:bold;">{}%</span>', color, pct)
    porcentaje_merma_badge.short_description = "% Merma"

    def estado_estudio_badge(self, obj):
        if hasattr(obj, 'estudio_previo'):
            estado = obj.estudio_previo.estado
            color = "#2e7d32" if estado == 'APROBADO' else "#e65100" if estado == 'EN_REVISION' else "#c62828"
            return format_html('<span style="color:{}; font-weight:bold;">{}</span>', color, estado)
        return format_html('<span style="color:#757575;">SIN ESTUDIO</span>')
    estado_estudio_badge.short_description = "Estudio Previo (M5)"

    def peso_restante_display(self, obj):
        return f"{obj.peso_restante_kg} kg"
    peso_restante_display.short_description = "Contenido Restante Calculado"

    def total_merma_display(self, obj):
        return f"{obj.total_merma_kg} kg"
    total_merma_display.short_description = "Total Merma Acumulada"

    def porcentaje_merma_display(self, obj):
        return f"{obj.porcentaje_merma_actual}%"
    porcentaje_merma_display.short_description = "Porcentaje de Merma Actual"


@admin.register(EstudioPrevio)
class EstudioPrevioAdmin(admin.ModelAdmin):
    list_display = ('lote', 'fecha_estudio', 'peso_calibrado_kg', 'porcentaje_pureza', 'responsable_estudio', 'estado_badge', 'supervisor_aprobador')
    list_filter = ('estado', 'fecha_estudio')
    search_fields = ('lote__codigo_lote', 'responsable_estudio__username', 'supervisor_aprobador__username')
    readonly_fields = ('fecha_aprobacion',)
    actions = ['aprobar_estudios_seleccionados']

    def estado_badge(self, obj):
        colores = {
            'APROBADO': '#2e7d32',
            'EN_REVISION': '#ef6c00',
            'BORRADOR': '#0277bd',
            'RECHAZADO': '#c62828'
        }
        color = colores.get(obj.estado, '#000000')
        return format_html('<strong style="color: {};">{}</strong>', color, obj.get_estado_display())
    estado_badge.short_description = "Estado de Aprobación"

    @admin.action(description="Aprobar Estudios Previos seleccionados (Supervisión)")
    def aprobar_estudios_seleccionados(self, request, queryset):
        # Validación de permisos por rol en acción personalizada
        if not (request.user.is_superuser or (hasattr(request.user, 'perfil') and request.user.perfil.rol in ['SUPERVISOR', 'ENCARGADO'])):
            self.message_user(request, "Permiso denegado: Solo Supervisores o Encargados pueden aprobar estudios técnicos.", level='ERROR')
            return

        actualizados = queryset.update(
            estado='APROBADO',
            supervisor_aprobador=request.user,
            fecha_aprobacion=timezone.now()
        )
        self.message_user(request, f"Se han aprobado satisfactoriamente {actualizados} estudios previos.")


@admin.register(Maquina)
class MaquinaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo', 'capacidad_max_kg', 'activa')
    list_filter = ('tipo', 'activa')
    search_fields = ('codigo', 'nombre', 'tipo')


@admin.register(Proceso)
class ProcesoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'temperatura_operacion_c')
    search_fields = ('codigo', 'nombre')


@admin.register(RegistroMerma)
class RegistroMermaAdmin(admin.ModelAdmin):
    list_display = ('id', 'lote', 'proceso', 'maquina', 'peso_merma_kg', 'tipo_merma', 'operador', 'fecha_registro')
    list_filter = ('tipo_merma', 'proceso', 'maquina', 'fecha_registro')
    search_fields = ('lote__codigo_lote', 'observaciones', 'operador__username')
    date_hierarchy = 'fecha_registro'

    def save_model(self, request, obj, form, change):
        if not obj.operador_id:
            obj.operador = request.user
        obj.full_clean()  # Ejecución de validaciones de negocio antes de persistir
        super().save_model(request, obj, form, change)
