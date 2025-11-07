from django import forms
from .models import Cliente
from core.forms_mixins import SmartCleanMixin

class ClienteForm(SmartCleanMixin, forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'nacionalidad': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'referencia_1': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_ref_1': forms.TextInput(attrs={'class': 'form-control'}),
            'referencia_2': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_ref_2': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
