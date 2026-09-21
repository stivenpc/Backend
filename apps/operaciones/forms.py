from django import forms
from .models import Material, LoteMaterial, EstudioPrevio, Maquina, Proceso, RegistroMerma

class LoteMaterialForm(forms.ModelForm):
    class Meta:
        model = LoteMaterial
        fields = ['codigo_lote', 'material', 'peso_inicial_kg', 'proveedor', 'fecha_ingreso', 'observaciones']
        widgets = {
            'codigo_lote': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. LOT-2026-AL01'}),
            'material': forms.Select(attrs={'class': 'form-select'}),
            'peso_inicial_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'proveedor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del proveedor o procedencia'}),
            'fecha_ingreso': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas sobre el lote...'}),
        }

    def clean_peso_inicial_kg(self):
        peso = self.cleaned_data.get('peso_inicial_kg')
        if peso is not None and peso <= 0:
            raise forms.ValidationError("El peso inicial ingresado debe ser mayor a 0 kg.")
        return peso


class EstudioPrevioForm(forms.ModelForm):
    class Meta:
        model = EstudioPrevio
        fields = [
            'lote', 'fecha_estudio', 'peso_calibrado_kg', 'porcentaje_pureza',
            'porcentaje_humedad', 'tolerancia_merma_max_pct', 'observaciones_metrologicas'
        ]
        widgets = {
            'lote': forms.Select(attrs={'class': 'form-select'}),
            'fecha_estudio': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'peso_calibrado_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'porcentaje_pureza': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '99.00'}),
            'porcentaje_humedad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.50'}),
            'tolerancia_merma_max_pct': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '8.00'}),
            'observaciones_metrologicas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detalles de calibración de báscula...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si es creación, mostrar sólo lotes que no tengan estudio previo asignado
        if not self.instance.pk:
            lotes_con_estudio = EstudioPrevio.objects.values_list('lote_id', flat=True)
            self.fields['lote'].queryset = LoteMaterial.objects.exclude(id__in=lotes_con_estudio)


class AprobarEstudioPrevioForm(forms.ModelForm):
    class Meta:
        model = EstudioPrevio
        fields = ['estado', 'observaciones_metrologicas']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'observaciones_metrologicas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_estado(self):
        estado = self.cleaned_data.get('estado')
        if estado not in ['APROBADO', 'RECHAZADO']:
            raise forms.ValidationError("El supervisor debe seleccionar APROBADO o RECHAZADO.")
        return estado


class RegistroMermaForm(forms.ModelForm):
    class Meta:
        model = RegistroMerma
        fields = ['lote', 'proceso', 'maquina', 'peso_merma_kg', 'tipo_merma', 'observaciones']
        widgets = {
            'lote': forms.Select(attrs={'class': 'form-select'}),
            'proceso': forms.Select(attrs={'class': 'form-select'}),
            'maquina': forms.Select(attrs={'class': 'form-select'}),
            'peso_merma_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'tipo_merma': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Causa del desecho o detalles del turno...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar máquinas activas
        self.fields['maquina'].queryset = Maquina.objects.filter(activa=True)
        # Filtrar solo lotes con estudio previo aprobado (facilitar UI y orientar al usuario)
        self.fields['lote'].queryset = LoteMaterial.objects.filter(estudio_previo__estado='APROBADO')
        self.fields['lote'].help_text = "Únicamente se listan lotes con Estudio Previo APROBADO por Supervisión."
