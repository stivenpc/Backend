from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Count
from django.utils import timezone

from .models import Material, LoteMaterial, EstudioPrevio, Maquina, Proceso, RegistroMerma
from .forms import LoteMaterialForm, EstudioPrevioForm, AprobarEstudioPrevioForm, RegistroMermaForm
from apps.usuarios.decorators import rol_requerido, supervisor_o_encargado_requerido, encargado_requerido
from apps.auditoria.utils import registrar_log
from apps.auditoria.models import LogAuditoria

# ==============================================================================
# DASHBOARD PRINCIPAL
# ==============================================================================
@login_required
def dashboard_view(request):
    total_lotes = LoteMaterial.objects.count()
    total_peso_ingresado = LoteMaterial.objects.aggregate(total=Sum('peso_inicial_kg'))['total'] or Decimal('0.00')
    total_merma = RegistroMerma.objects.aggregate(total=Sum('peso_merma_kg'))['total'] or Decimal('0.00')
    saldo_global = total_peso_ingresado - total_merma
    
    estudios_pendientes = EstudioPrevio.objects.filter(estado__in=['BORRADOR', 'EN_REVISION']).count()
    ultimas_mermas = RegistroMerma.objects.select_related('lote', 'proceso', 'maquina', 'operador').order_by('-fecha_registro')[:6]
    lotes_recientes = LoteMaterial.objects.select_related('material').prefetch_related('mermas').order_by('-fecha_ingreso')[:5]

    contexto = {
        'total_lotes': total_lotes,
        'total_peso_ingresado': total_peso_ingresado,
        'total_merma': total_merma,
        'saldo_global': max(Decimal('0.00'), saldo_global),
        'estudios_pendientes': estudios_pendientes,
        'ultimas_mermas': ultimas_mermas,
        'lotes_recientes': lotes_recientes,
    }
    return render(request, 'operaciones/dashboard.html', contexto)


# ==============================================================================
# CRUD LOTES DE MATERIALES (M1 / Criterio 2.1.3)
# ==============================================================================
@login_required
def lote_list(request):
    lotes = LoteMaterial.objects.select_related('material').prefetch_related('mermas').all()
    return render(request, 'operaciones/lote_list.html', {'lotes': lotes})

@login_required
def lote_detail(request, pk):
    lote = get_object_or_404(LoteMaterial.objects.select_related('material'), pk=pk)
    mermas = lote.mermas.select_related('proceso', 'maquina', 'operador').order_by('-fecha_registro')
    return render(request, 'operaciones/lote_detail.html', {'lote': lote, 'mermas': mermas})

@login_required
@rol_requerido('SUPERVISOR', 'ENCARGADO')
def lote_create(request):
    if request.method == 'POST':
        form = LoteMaterialForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                lote = form.save()
                registrar_log(
                    accion='CREATE',
                    tabla_afectada='operaciones_lotematerial',
                    registro_id=lote.id,
                    detalles=f"Ingreso de nuevo lote {lote.codigo_lote} ({lote.material.nombre}) con {lote.peso_inicial_kg} kg.",
                    usuario=request.user
                )
            messages.success(request, f"Lote {lote.codigo_lote} registrado exitosamente. Recuerde crear el Estudio Previo obligatorio.")
            return redirect('operaciones:lote_detail', pk=lote.pk)
        else:
            messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = LoteMaterialForm()
    return render(request, 'operaciones/lote_form.html', {'form': form, 'titulo': 'Registrar Nuevo Lote de Material'})

@login_required
@rol_requerido('SUPERVISOR', 'ENCARGADO')
def lote_update(request, pk):
    lote = get_object_or_404(LoteMaterial, pk=pk)
    if request.method == 'POST':
        form = LoteMaterialForm(request.POST, instance=lote)
        if form.is_valid():
            with transaction.atomic():
                lote = form.save()
                registrar_log(
                    accion='UPDATE',
                    tabla_afectada='operaciones_lotematerial',
                    registro_id=lote.id,
                    detalles=f"Modificación administrativa del lote {lote.codigo_lote}.",
                    usuario=request.user
                )
            messages.success(request, f"Lote {lote.codigo_lote} actualizado correctamente.")
            return redirect('operaciones:lote_detail', pk=lote.pk)
        else:
            messages.error(request, "Error al actualizar el lote.")
    else:
        form = LoteMaterialForm(instance=lote)
    return render(request, 'operaciones/lote_form.html', {'form': form, 'titulo': f'Editar Lote {lote.codigo_lote}'})

@login_required
@encargado_requerido
def lote_delete(request, pk):
    lote = get_object_or_404(LoteMaterial, pk=pk)
    if request.method == 'POST':
        codigo = lote.codigo_lote
        with transaction.atomic():
            lote.delete()
            registrar_log(
                accion='DELETE',
                tabla_afectada='operaciones_lotematerial',
                registro_id=pk,
                detalles=f"Eliminación física del lote {codigo} por Encargado de Planta.",
                usuario=request.user
            )
        messages.success(request, f"Lote {codigo} eliminado del sistema.")
        return redirect('operaciones:lote_list')
    return render(request, 'operaciones/confirmar_eliminar.html', {'objeto': lote, 'tipo': 'Lote de Material'})


# ==============================================================================
# CRUD ESTUDIO PREVIO DE CONTENIDO (M5 / Gatekeeper Obligatorio)
# ==============================================================================
@login_required
def estudio_list(request):
    estudios = EstudioPrevio.objects.select_related('lote__material', 'responsable_estudio', 'supervisor_aprobador').all()
    return render(request, 'operaciones/estudio_list.html', {'estudios': estudios})

@login_required
def estudio_detail(request, pk):
    estudio = get_object_or_404(EstudioPrevio.objects.select_related('lote__material', 'responsable_estudio', 'supervisor_aprobador'), pk=pk)
    return render(request, 'operaciones/estudio_detail.html', {'estudio': estudio})

@login_required
def estudio_create(request):
    """Cualquier operador o supervisor puede ingresar los parámetros del pesaje previo."""
    if request.method == 'POST':
        form = EstudioPrevioForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                estudio = form.save(commit=False)
                estudio.responsable_estudio = request.user
                estudio.estado = 'EN_REVISION'
                estudio.save()
                registrar_log(
                    accion='CREATE',
                    tabla_afectada='operaciones_estudioprevio',
                    registro_id=estudio.id,
                    detalles=f"Registro de Estudio Previo para el lote {estudio.lote.codigo_lote} con peso calibrado {estudio.peso_calibrado_kg} kg.",
                    usuario=request.user
                )
            messages.success(request, f"Estudio previo para lote {estudio.lote.codigo_lote} registrado. Queda pendiente de Aprobación por Supervisión.")
            return redirect('operaciones:estudio_detail', pk=estudio.pk)
        else:
            messages.error(request, "Error en los datos del estudio previo.")
    else:
        form = EstudioPrevioForm()
    return render(request, 'operaciones/estudio_form.html', {'form': form, 'titulo': 'Registrar Estudio Previo de Contenido (M5)'})

@login_required
@supervisor_o_encargado_requerido
def estudio_aprobar(request, pk):
    """Aprobación técnica obligatoria por Supervisor o Encargado."""
    estudio = get_object_or_404(EstudioPrevio, pk=pk)
    if request.method == 'POST':
        form = AprobarEstudioPrevioForm(request.POST, instance=estudio)
        if form.is_valid():
            with transaction.atomic():
                estudio = form.save(commit=False)
                estudio.supervisor_aprobador = request.user
                estudio.fecha_aprobacion = timezone.now()
                estudio.save()
                registrar_log(
                    accion='APROBAR',
                    tabla_afectada='operaciones_estudioprevio',
                    registro_id=estudio.id,
                    detalles=f"Dictamen técnico del estudio del lote {estudio.lote.codigo_lote}: {estudio.estado} por {request.user.username}.",
                    usuario=request.user
                )
            messages.success(request, f"Estudio previo dictaminado como: {estudio.get_estado_display()}.")
            return redirect('operaciones:estudio_detail', pk=estudio.pk)
    else:
        form = AprobarEstudioPrevioForm(instance=estudio)
    return render(request, 'operaciones/estudio_aprobar.html', {'form': form, 'estudio': estudio})


# ==============================================================================
# CRUD REGISTRO DE MERMA ESPECÍFICA (M4 / Criterio 2.1.3)
# ==============================================================================
@login_required
def merma_list(request):
    mermas = RegistroMerma.objects.select_related('lote__material', 'proceso', 'maquina', 'operador').all()
    
    # Filtros simples opcionales
    maquina_id = request.GET.get('maquina')
    proceso_id = request.GET.get('proceso')
    tipo_merma = request.GET.get('tipo')

    if maquina_id:
        mermas = mermas.filter(maquina_id=maquina_id)
    if proceso_id:
        mermas = mermas.filter(proceso_id=proceso_id)
    if tipo_merma:
        mermas = mermas.filter(tipo_merma=tipo_merma)

    maquinas = Maquina.objects.filter(activa=True)
    procesos = Proceso.objects.all()

    contexto = {
        'mermas': mermas,
        'maquinas': maquinas,
        'procesos': procesos,
        'filtro_maquina': maquina_id,
        'filtro_proceso': proceso_id,
        'filtro_tipo': tipo_merma,
    }
    return render(request, 'operaciones/merma_list.html', contexto)

@login_required
def merma_detail(request, pk):
    merma = get_object_or_404(RegistroMerma.objects.select_related('lote__material', 'proceso', 'maquina', 'operador'), pk=pk)
    return render(request, 'operaciones/merma_detail.html', {'merma': merma})

@login_required
def merma_create(request):
    """
    Registro de Merma Específica.
    Valida el candado del Estudio Previo Aprobado y descuenta automáticamente el remanente.
    """
    if request.method == 'POST':
        form = RegistroMermaForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    merma = form.save(commit=False)
                    merma.operador = request.user
                    merma.full_clean()  # Ejecuta validaciones del modelo (Gatekeeper y saldo)
                    merma.save()
                    
                    registrar_log(
                        accion='CREATE',
                        tabla_afectada='operaciones_registromerma',
                        registro_id=merma.id,
                        detalles=(
                            f"Registro de merma de {merma.peso_merma_kg} kg en lote {merma.lote.codigo_lote} "
                            f"| Máquina: {merma.maquina.codigo} | Proceso: {merma.proceso.codigo} "
                            f"| Tipo: {merma.tipo_merma}."
                        ),
                        usuario=request.user
                    )
                messages.success(
                    request,
                    f"Merma de {merma.peso_merma_kg} kg registrada exitosamente en {merma.maquina.nombre}. "
                    f"Contenido restante del lote: {merma.lote.peso_restante_kg} kg."
                )
                return redirect('operaciones:merma_detail', pk=merma.pk)
            except Exception as e:
                messages.error(request, f"No se pudo guardar la merma: {str(e)}")
        else:
            messages.error(request, "Revise los campos indicados en el formulario.")
    else:
        form = RegistroMermaForm()
    return render(request, 'operaciones/merma_form.html', {'form': form, 'titulo': 'Registrar Merma Específica (M4)'})

@login_required
@supervisor_o_encargado_requerido
def merma_update(request, pk):
    merma = get_object_or_404(RegistroMerma, pk=pk)
    if request.method == 'POST':
        form = RegistroMermaForm(request.POST, instance=merma)
        if form.is_valid():
            try:
                with transaction.atomic():
                    merma = form.save(commit=False)
                    merma.full_clean()
                    merma.save()
                    registrar_log(
                        accion='UPDATE',
                        tabla_afectada='operaciones_registromerma',
                        registro_id=merma.id,
                        detalles=f"Modificación técnica de pesaje de merma ID {merma.id} a {merma.peso_merma_kg} kg.",
                        usuario=request.user
                    )
                messages.success(request, f"Registro de merma {merma.id} actualizado.")
                return redirect('operaciones:merma_detail', pk=merma.pk)
            except Exception as e:
                messages.error(request, f"Error al actualizar la merma: {str(e)}")
    else:
        form = RegistroMermaForm(instance=merma)
    return render(request, 'operaciones/merma_form.html', {'form': form, 'titulo': f'Editar Registro de Merma #{merma.id}'})

@login_required
@encargado_requerido
def merma_delete(request, pk):
    merma = get_object_or_404(RegistroMerma, pk=pk)
    if request.method == 'POST':
        peso = merma.peso_merma_kg
        lote_cod = merma.lote.codigo_lote
        with transaction.atomic():
            merma.delete()
            registrar_log(
                accion='DELETE',
                tabla_afectada='operaciones_registromerma',
                registro_id=pk,
                detalles=f"Anulación de registro de merma de {peso} kg en lote {lote_cod}.",
                usuario=request.user
            )
        messages.success(request, f"Registro de merma anulado. El saldo del lote {lote_cod} ha sido restablecido.")
        return redirect('operaciones:merma_list')
    return render(request, 'operaciones/confirmar_eliminar.html', {'objeto': merma, 'tipo': 'Registro de Merma'})


# ==============================================================================
# VISTA DE AUDITORÍA FORENSE (M3 / Criterio 2.1.4)
# ==============================================================================
@login_required
@supervisor_o_encargado_requerido
def auditoria_list(request):
    logs = LogAuditoria.objects.select_related('usuario').all()[:150]
    return render(request, 'auditoria/log_list.html', {'logs': logs})
