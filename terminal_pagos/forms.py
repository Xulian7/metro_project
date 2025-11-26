from django import forms
from .models import Factura, DetalleFactura, Pago


class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['cedula', 'placa', 'cliente']
        widgets = {
            'cedula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cédula del cliente'
            }),
            'placa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Placa del vehículo (opcional)'
            }),
            'cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del cliente'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Bloquear campos (pero enviables)
        self.fields['cedula'].widget.attrs['readonly'] = True
        self.fields['cliente'].widget.attrs['readonly'] = True



class DetalleFacturaForm(forms.ModelForm):
    class Meta:
        model = DetalleFactura
        fields = ['concepto', 'descripcion', 'valor_unitario', 'cantidad']
        widgets = {
            'concepto': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descripción o nota'}),
            'valor_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        concepto = cleaned_data.get('concepto')
        factura = self.instance.factura if self.instance.pk else self.initial.get('factura')

        if concepto == 'abono_inicial' and factura:
            existe = DetalleFactura.objects.filter(factura=factura, concepto='abono_inicial').exclude(pk=self.instance.pk).exists()
            if existe:
                raise forms.ValidationError("Ya existe un abono inicial en esta factura.")
        return cleaned_data


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['medio_pago', 'origen_nequi', 'valor', 'referencia']
        widgets = {
            'medio_pago': forms.Select(attrs={'class': 'form-select'}),
            'origen_nequi': forms.Select(attrs={'class': 'form-select'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'referencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de referencia o nota'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        medio = cleaned_data.get('medio_pago')
        origen = cleaned_data.get('origen_nequi')

        if medio == 'nequi' and not origen:
            raise forms.ValidationError("Debe seleccionar el origen si el medio de pago es Nequi.")
        return cleaned_data
