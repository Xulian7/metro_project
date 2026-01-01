from django import forms
from django.forms import inlineformset_factory
from .models import Factura, ItemFactura


class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ["placa", "nombre_cliente"]


class ItemFacturaForm(forms.ModelForm):
    class Meta:
        model = ItemFactura
        exclude = ("factura", "subtotal")


ItemFacturaFormSet = inlineformset_factory(
    Factura,
    ItemFactura,
    form=ItemFacturaForm,
    extra=1,
    can_delete=True,
)
