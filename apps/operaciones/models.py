from decimal import Decimal
from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

class Material(models.Model):
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código Material")
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la Aleación / Metal")
    descripcion = models.TextField(blank=True, verbose_name="Descripción Técnica")
    densidad_g_cm3 = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('2.70'), verbose_name="Densidad (g/cm³)")
    punto_fusion_c = models.IntegerField(default=660, verbose_name="Punto de Fusión (°C)")

    class Meta:
        verbose_name = "Material / Aleación"
        verbose_name_plural = "Materiales y Aleaciones"
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class LoteMaterial(models.Model):
    codigo_lote = models.CharField(max_length=30, unique=True, verbose_name="Código de Lote")
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name='lotes', verbose_name="Material")
    peso_inicial_kg = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Peso Inicial Ingresado (kg)")
    proveedor = models.CharField(max_length=120, verbose_name="Proveedor / Origen")
    fecha_ingreso = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Ingreso")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")

    class Meta:
        verbose_name = "Lote de Material"
        verbose_name_plural = "Lotes de Materiales (Inventario)"
        ordering = ['-fecha_ingreso']

    def __str__(self):
        return f"{self.codigo_lote} ({self.material.nombre}) - {self.peso_inicial_kg} kg"

    @property
    def total_merma_kg(self):
        """Calcula la suma acumulada de merma registrada para este lote (M1)."""
        resultado = self.mermas.aggregate(total=Sum('peso_merma_kg'))['total']
        return Decimal(str(resultado)) if resultado is not None else Decimal('0.00')

    @property
    def peso_restante_kg(self):
        """Calcula automáticamente el contenido restante del material (M1)."""
        return max(Decimal('0.00'), self.peso_inicial_kg - self.total_merma_kg)

    @property
    def porcentaje_merma_actual(self):
        """Calcula el porcentaje de merma acumulada."""
        if self.peso_inicial_kg and self.peso_inicial_kg > 0:
            pct = (self.total_merma_kg / self.peso_inicial_kg) * 100
            return round(pct, 2)
        return Decimal('0.00')

    @property
    def tiene_estudio_aprobado(self):
        """Verifica si el lote cuenta con el estudio previo obligatorio en estado APROBADO (M5)."""
        return hasattr(self, 'estudio_previo') and self.estudio_previo.estado == 'APROBADO'

    def clean(self):
        super().clean()
        if self.peso_inicial_kg is not None and self.peso_inicial_kg <= 0:
            raise ValidationError({'peso_inicial_kg': "El peso inicial del lote debe ser estrictamente mayor a 0 kg."})


class EstudioPrevio(models.Model):
    """
    Validación de Estudio Previo Obligatorio (M5 - Gatekeeper).
    Impide registrar mermas o consumos si los parámetros metrológicos no han sido aprobados por un Supervisor.
    """
    ESTADOS = (
        ('BORRADOR', 'Borrador / Registrado en Báscula'),
        ('EN_REVISION', 'En Revisión Técnica'),
        ('APROBADO', 'Aprobado por Supervisión'),
        ('RECHAZADO', 'Rechazado'),
    )

    lote = models.OneToOneField(LoteMaterial, on_delete=models.CASCADE, related_name='estudio_previo', verbose_name="Lote de Material")
    fecha_estudio = models.DateTimeField(default=timezone.now, verbose_name="Fecha y Hora de Pesaje Calibrado")
    peso_calibrado_kg = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Peso Verificado en Báscula Calibrada (kg)")
    porcentaje_pureza = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('99.00'), verbose_name="Pureza Estimada (%)")
    porcentaje_humedad = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.50'), verbose_name="Humedad Superficial (%)")
    tolerancia_merma_max_pct = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('8.00'), verbose_name="Tolerancia Máxima de Merma Admisible (%)")
    estado = models.CharField(max_length=20, choices=ESTADOS, default='BORRADOR', verbose_name="Estado de Aprobación")
    
    responsable_estudio = models.ForeignKey(User, on_delete=models.PROTECT, related_name='estudios_realizados', verbose_name="Técnico / Operador Responsable")
    supervisor_aprobador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='estudios_aprobados', verbose_name="Supervisor Aprobador")
    fecha_aprobacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Aprobación")
    observaciones_metrologicas = models.TextField(blank=True, verbose_name="Observaciones Metrológicas / Calibración")

    class Meta:
        verbose_name = "Estudio Previo de Contenido"
        verbose_name_plural = "Estudios Previos de Contenido (Gatekeeper M5)"
        ordering = ['-fecha_estudio']

    def __str__(self):
        return f"Estudio Previo: Lote {self.lote.codigo_lote} - Estado: {self.get_estado_display()}"

    def clean(self):
        super().clean()
        if self.peso_calibrado_kg is not None and self.peso_calibrado_kg <= 0:
            raise ValidationError({'peso_calibrado_kg': "El peso calibrado debe ser mayor a 0 kg."})
        if self.porcentaje_pureza is not None and not (0 <= self.porcentaje_pureza <= 100):
            raise ValidationError({'porcentaje_pureza': "El porcentaje de pureza debe encontrarse entre 0% y 100%."})
        if self.porcentaje_humedad is not None and not (0 <= self.porcentaje_humedad <= 100):
            raise ValidationError({'porcentaje_humedad': "El porcentaje de humedad debe encontrarse entre 0% y 100%."})


class Maquina(models.Model):
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código Máquina")
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la Máquina")
    tipo = models.CharField(max_length=60, verbose_name="Tipo / Tecnología")
    capacidad_max_kg = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('500.00'), verbose_name="Capacidad Máxima (kg)")
    activa = models.BooleanField(default=True, verbose_name="Activa / Operativa")

    class Meta:
        verbose_name = "Máquina de Planta"
        verbose_name_plural = "Maquinarias de Fundición"
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre} ({self.tipo})"


class Proceso(models.Model):
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código Proceso")
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Proceso")
    temperatura_operacion_c = models.IntegerField(null=True, blank=True, verbose_name="Temperatura Operación (°C)")
    descripcion = models.TextField(blank=True, verbose_name="Descripción del Proceso")

    class Meta:
        verbose_name = "Proceso de Fundición"
        verbose_name_plural = "Procesos Operativos"
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class RegistroMerma(models.Model):
    """
    Módulo de Registro de Merma Específica (M4).
    Asocia directamente la merma a: proceso, máquina, lote y cantidad.
    """
    TIPOS_MERMA = (
        ('ESCORIA', 'Escoria de Fusión / Horno'),
        ('VIRUTA', 'Viruta de Mecanizado / Torneado'),
        ('REBABA', 'Rebaba y Canales de Colada'),
        ('DEFECTO', 'Pieza Defectuosa / Descarte de Moldeo'),
        ('VOLATILIZACION', 'Pérdida por Oxidación / Volatilización'),
    )

    lote = models.ForeignKey(LoteMaterial, on_delete=models.CASCADE, related_name='mermas', verbose_name="Lote de Material")
    proceso = models.ForeignKey(Proceso, on_delete=models.PROTECT, related_name='mermas', verbose_name="Proceso Realizado")
    maquina = models.ForeignKey(Maquina, on_delete=models.PROTECT, related_name='mermas', verbose_name="Máquina Utilizada")
    peso_merma_kg = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Peso de Merma (kg)")
    tipo_merma = models.CharField(max_length=30, choices=TIPOS_MERMA, default='ESCORIA', verbose_name="Tipo de Merma")
    operador = models.ForeignKey(User, on_delete=models.PROTECT, related_name='mermas_registradas', verbose_name="Operador Registrador")
    fecha_registro = models.DateTimeField(default=timezone.now, verbose_name="Fecha y Hora de Registro")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones / Causa del Desperdicio")

    class Meta:
        verbose_name = "Registro de Merma Específica"
        verbose_name_plural = "Registros de Merma Específica (M4)"
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"Merma {self.peso_merma_kg} kg ({self.get_tipo_merma_display()}) - Lote {self.lote.codigo_lote} [{self.maquina.codigo}]"

    def clean(self):
        super().clean()
        # 1. Validación de Estudio Previo Obligatorio (M5)
        if not hasattr(self.lote, 'estudio_previo') or self.lote.estudio_previo.estado != 'APROBADO':
            raise ValidationError(
                "VALIDACIÓN DE ESTUDIO PREVIO OBLIGATORIO: "
                "No está permitido registrar merma para este lote de material porque no cuenta "
                "con un Estudio Previo de Contenido en estado APROBADO por el Supervisor."
            )

        # 2. Validación de Peso de Merma Estrictamente Positivo
        if self.peso_merma_kg is not None and self.peso_merma_kg <= 0:
            raise ValidationError({'peso_merma_kg': "El peso de la merma debe ser estrictamente mayor a 0 kg."})

        # 3. Validación de Balance de Inventario: No exceder contenido disponible (M1)
        if self.lote and self.peso_merma_kg is not None:
            # Si estamos editando un registro existente, descontamos su valor previo para comparar
            merma_existente_otro = self.lote.mermas.exclude(pk=self.pk).aggregate(total=Sum('peso_merma_kg'))['total']
            total_otras_mermas = Decimal(str(merma_existente_otro)) if merma_existente_otro is not None else Decimal('0.00')
            saldo_disponible = self.lote.peso_inicial_kg - total_otras_mermas

            if self.peso_merma_kg > saldo_disponible:
                raise ValidationError({
                    'peso_merma_kg': (
                        f"La merma ingresada ({self.peso_merma_kg} kg) excede el saldo restante "
                        f"disponible en el lote ({saldo_disponible} kg)."
                    )
                })
