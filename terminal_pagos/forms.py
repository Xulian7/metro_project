from django import forms
from .models import Transaccion

class TransaccionForm(forms.ModelForm):
    class Meta:
        model = Transaccion
        fields = ['tipo_pago', 'placa', 'cedula', 'cliente', 'valor', 'medio_pago', 'origen', 'referencia', 'fecha_ingreso']
        widgets = {
            'fecha_ingreso': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        medio_pago = cleaned_data.get('medio_pago')
        origen = cleaned_data.get('origen')

        if medio_pago == 'nequi' and not origen:
            self.add_error('origen', 'Debe seleccionar un origen si el medio de pago es Nequi.')

        return cleaned_data

    def clean_cliente(self):
        cliente = self.cleaned_data.get('cliente', '')
        return cliente.title()  # fuerza Nombre Propio

    def clean_placa(self):
        placa = self.cleaned_data.get('placa', '')
        return placa.upper()  # fuerza mayúsculas
