from django import forms
from django.forms import inlineformset_factory

from .models import (
    Factura,
    ItemFactura,
    Cuenta,
    OrigenFondo,
    CanalPago,
    OrigenCanal,
    PagoFactura,
)

from arrendamientos.models import Contrato


# =========================
# SELECT PERSONALIZADO CONTRATO
# =========================
class ContratoSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(
            name, value, label, selected, index, subindex=subindex, attrs=attrs
        )

        if value and hasattr(value, "value"):
            try:
                contrato = Contrato.objects.get(pk=value.value)
                option["attrs"]["data-tarifa"] = contrato.tarifa
            except Contrato.DoesNotExist:
                pass

        return option


# =========================
# FACTURA
# =========================
class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ["contrato"]
        widgets = {
            "contrato": ContratoSelect()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["contrato"].queryset = Contrato.objects.select_related(
            "vehiculo", "cliente"
        )

        self.fields["contrato"].label_from_instance = (
            lambda obj: f"{obj.vehiculo.placa} — {obj.cliente.nombre}"
        )


# =========================
# ITEMS DE FACTURA
# =========================
class ItemFacturaForm(forms.ModelForm):
    descripcion = forms.ChoiceField(choices=[], required=True)

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


# =========================
# CUENTAS
# =========================
class CuentaForm(forms.ModelForm):
    class Meta:
        model = Cuenta
        fields = ["nombre", "activa"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "activa": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


# =========================
# ORIGEN DE FONDOS
# =========================
class OrigenFondoForm(forms.ModelForm):
    class Meta:
        model = OrigenFondo
        fields = ["nombre", "tipo", "cuenta_principal", "activo"]


# =========================
# CANAL DE PAGO
# =========================
class CanalPagoForm(forms.ModelForm):
    class Meta:
        model = CanalPago
        fields = [
            "codigo",
            "nombre",
            "requiere_referencia",
            "es_egreso",
            "activo",
        ]


# =========================
# CONFIGURACIÓN ORIGEN + CANAL
# =========================
class OrigenCanalForm(forms.ModelForm):
    class Meta:
        model = OrigenCanal
        fields = [
            "origen",
            "canal",
            "cuenta_debito",
            "cuenta_credito",
            "activo",
        ]


# =========================
# PAGO DE FACTURA
# =========================
class PagoFacturaForm(forms.ModelForm):
    class Meta:
        model = PagoFactura
        fields = [
            "origen_canal",
            "valor",
            "referencia",
        ]
