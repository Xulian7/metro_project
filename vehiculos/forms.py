from django import forms
from .models import Vehiculo, Marca
from core.forms_mixins import SmartCleanMixin

class VehiculoForm(SmartCleanMixin, forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = [
            'placa', 'marca', 'modelo', 'serie','color', 'propietario',
            'numero_motor', 'numero_chasis', 'linea_gps', 'actualizacion_soat'
        ]

        widgets = {
            'placa': forms.TextInput(attrs={'class': 'form-control', 'style': 'text-transform: uppercase;'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'serie': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
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

        if 'estado_obs' in self.fields:
            estado_actual = self.instance.estado if self.instance else None

            if estado_actual != "Inactivo":
                self.fields['estado_obs'].widget.attrs['disabled'] = True
                self.fields['estado_obs'].required = False
            else:
                self.fields['estado_obs'].widget.attrs.pop('disabled', None)
                self.fields['estado_obs'].required = True


    def clean(self):
        cleaned_data = super().clean()

        if 'estado' in cleaned_data and 'estado_obs' in cleaned_data:
            estado = cleaned_data.get('estado')
            estado_obs = cleaned_data.get('estado_obs')

            if estado != "Inactivo":
                cleaned_data['estado_obs'] = None
            else:
                if not estado_obs:
                    raise forms.ValidationError(
                        "Debes seleccionar una observación de estado cuando el vehículo está Inactivo."
                    )

        return cleaned_data


class MarcaForm(SmartCleanMixin, forms.ModelForm):
    class Meta:
        model = Marca
        fields = ["nombre", "parent"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "parent": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Mostrar solo marcas como posibles padres (no series)
        self.fields["parent"].queryset = Marca.objects.filter(parent__isnull=True) # type: ignore
        self.fields["parent"].required = False