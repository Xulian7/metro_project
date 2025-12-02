from django import forms
from .models import Vehiculo

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = '__all__'
        widgets = {
            'placa': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'serie': forms.TextInput(attrs={'class': 'form-control'}),
            'propietario': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_motor': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_chasis': forms.TextInput(attrs={'class': 'form-control'}),
            'linea_gps': forms.TextInput(attrs={'class': 'form-control'}),
            'actualizacion_soat': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'estado_obs': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Obtenemos el estado actual (si existe)
        estado_actual = self.instance.estado if self.instance else None
        # Si el estado NO es "Inactivo", deshabilitamos estado_obs y lo dejamos vacío
        if estado_actual != "Inactivo":
            self.fields['estado_obs'].widget.attrs['disabled'] = True
            self.fields['estado_obs'].required = False
        else:
            self.fields['estado_obs'].widget.attrs.pop('disabled', None)
            self.fields['estado_obs'].required = True

    def clean(self):
        cleaned_data = super().clean()
        estado = cleaned_data.get('estado')
        estado_obs = cleaned_data.get('estado_obs')

        # Lógica de validación
        if estado != "Inactivo":
            cleaned_data['estado_obs'] = None  # Se fuerza a NULL
        else:
            if not estado_obs:
                raise forms.ValidationError(
                    "Debes seleccionar una observación de estado cuando el vehículo está Inactivo."
                )
        return cleaned_data
