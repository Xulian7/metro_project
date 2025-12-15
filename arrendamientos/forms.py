from django import forms
from .models import Contrato
from clientes.models import Cliente
from vehiculos.models import Vehiculo

class ContratoForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.exclude(tipo='Inversionista'),
        widget=forms.Select(attrs={'class': 'form-select select2', 'data-placeholder': 'Buscar cliente...'})
    )
    
    cedula = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': True
        })
    )
    
    vehiculo = forms.ModelChoiceField(
        queryset=Vehiculo.objects.filter(estado='Vitrina'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Contrato
        fields = [
            'cliente', 'vehiculo', 'fecha_inicio', 'cuota_inicial',
            'tarifa', 'dias_contrato', 'visitador', 'tipo_contrato',
            'estado', 'motivo', 
        ]
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'cuota_inicial': forms.NumberInput(attrs={'class': 'form-control'}),
            'tarifa': forms.NumberInput(attrs={'class': 'form-control'}),
            'dias_contrato': forms.NumberInput(attrs={'class': 'form-control'}),
            'visitador': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_contrato': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'motivo': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instancia = self.instance

        # --- Lógica para motivo ---
        if instancia and instancia.estado == "Inactivo":
            # Habilitado
            self.fields['motivo'].widget.attrs.pop('disabled', None)
            self.fields['motivo'].required = True
        else:
            # Deshabilitado
            self.fields['motivo'].widget.attrs['disabled'] = True
            self.fields['motivo'].required = False

    def clean(self):
        cleaned_data = super().clean()
        estado = cleaned_data.get('estado')
        motivo = cleaned_data.get('motivo')

        # Si el contrato NO está inactivo, motivo debe ser NULL
        if estado != "Inactivo":
            cleaned_data['motivo'] = None
        else:
            # Si está Inactivo, motivo es obligatorio
            if not motivo:
                raise forms.ValidationError("Debes seleccionar un motivo si el contrato está inactivo.")

        return cleaned_data
