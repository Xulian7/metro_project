from django import forms
from django.forms import inlineformset_factory
from .models import Factura, ItemFactura, PagoFactura


# =========================
# FACTURA
# =========================
class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = (
            "contrato",
            "estado",
        )


# =========================
# ÍTEMS DE FACTURA
# =========================
class ItemFacturaForm(forms.ModelForm):
    class Meta:
        model = ItemFactura
        fields = (
            "tipo_item",
            "descripcion",
            "cantidad",
            "valor_unitario",
        )

    def clean(self):
        cleaned_data = super().clean()

        cantidad = cleaned_data.get("cantidad")
        valor = cleaned_data.get("valor_unitario")

        if cantidad is None or cantidad <= 0:
            raise forms.ValidationError(
                "La cantidad debe ser mayor que cero."
            )

        if valor is None or valor <= 0:
            raise forms.ValidationError(
                "El valor unitario debe ser mayor que cero."
            )

        return cleaned_data


ItemFacturaFormSet = inlineformset_factory(
    Factura,
    ItemFactura,
    form=ItemFacturaForm,
    extra=1,        # al menos una línea visible
    can_delete=True # permite borrar ítems
)


# =========================
# PAGOS DE FACTURA (OPCIONAL)
# =========================
class PagoFacturaForm(forms.ModelForm):
    class Meta:
        model = PagoFactura
        fields = (
            "medio_pago",
            "valor",
            "referencia",
        )


PagoFacturaFormSet = inlineformset_factory(
    Factura,
    PagoFactura,
    form=PagoFacturaForm,
    extra=1,
    can_delete=True
)
