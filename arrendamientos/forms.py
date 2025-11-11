from django import forms
from .models import Contrato
from clientes.models import Cliente
from vehiculos.models import Vehiculo

class ContratoForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select select2', 'data-placeholder': 'Buscar cliente...'})
    )
    vehiculo = forms.ModelChoiceField(
        queryset=Vehiculo.objects.filter(estado='Inactivo'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Contrato
        fields = ['cliente', 'vehiculo', 'fecha_inicio', 'cuota_inicial', 'tarifa', 'dias_contrato', 'visitador']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'cuota_inicial': forms.NumberInput(attrs={'class': 'form-control'}),
            'tarifa': forms.NumberInput(attrs={'class': 'form-control'}),
            'dias_contrato': forms.NumberInput(attrs={'class': 'form-control'}),
            'visitador': forms.TextInput(attrs={'class': 'form-control'}),
        }
