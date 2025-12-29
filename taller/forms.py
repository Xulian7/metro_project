from django import forms
from .models import Servicio, Mecanico
from core.forms_mixins import SmartCleanMixin

class ServicioForm(SmartCleanMixin, forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre_servicio', 'valor']
        widgets = {
            'nombre_servicio': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class MecanicoForm(SmartCleanMixin, forms.ModelForm):
    class Meta:
        model = Mecanico
        fields = ['nombre', 'identificacion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'identificacion': forms.TextInput(attrs={'class': 'form-control'}),
        }
