from django import forms
from .models import Producto, Proveedor, Movimiento

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = '__all__'


class MovimientoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = '__all__'
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control'}),
            'factura_referencia': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        factura = cleaned_data.get('factura_referencia')

        # 🧩 Tipos que requieren referencia obligatoria
        tipos_con_factura = [
            'ingreso_compra',
            'salida_venta',
            'ingreso_devolucion_cliente',
            'salida_devolucion_proveedor',
        ]

        if tipo in tipos_con_factura and not factura:
            raise forms.ValidationError(
                "Debe ingresar una factura o referencia para este tipo de movimiento."
            )

        return cleaned_data
