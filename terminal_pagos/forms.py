from django import forms
from django.forms import inlineformset_factory


from .models import (
    Factura,
    ItemFactura,
    Cuenta,
    MedioPago,
    CanalPago,
    ConfiguracionPago,
    PagoFactura,
)

from arrendamientos.models import Contrato


# =========================
# SELECT PERSONALIZADO CONTRATO
# =========================
class ContratoSelect(forms.Select):
    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
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
    descripcion = forms.CharField(required=True)
    # descripcion = forms.ChoiceField(choices=[], required=True)

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
# CUENTAS DESTINO
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
# MEDIOS DE PAGO
# =========================
class MedioPagoForm(forms.ModelForm):
    class Meta:
        model = MedioPago
        fields = ["nombre", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


# =========================
# CANALES DE PAGO
# =========================
class CanalPagoForm(forms.ModelForm):
    class Meta:
        model = CanalPago
        fields = [
            "medio",
            "nombre",
            "requiere_referencia",
            "activo",
        ]
        widgets = {
            "medio": forms.Select(attrs={"class": "form-control"}),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "requiere_referencia": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


# =========================
# CONFIGURACIÓN DE PAGO
# MEDIO → CUENTA
# =========================
class ConfiguracionPagoForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionPago
        fields = [
            "medio",           # 🔑 ESTE CAMPO FALTABA
            "cuenta_destino",
            "activo",
        ]
        widgets = {
            "medio": forms.Select(attrs={"class": "form-control"}),
            "cuenta_destino": forms.Select(attrs={"class": "form-control"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }




# =========================
# PAGO DE FACTURA
# =========================
class PagoFacturaForm(forms.ModelForm):
    class Meta:
        model = PagoFactura
        fields = [
            "configuracion",
            "valor",
            "referencia",
        ]
        widgets = {
            "configuracion": forms.Select(attrs={"class": "form-control"}),
            "valor": forms.NumberInput(attrs={"class": "form-control"}),
            "referencia": forms.TextInput(attrs={"class": "form-control"}),
        }
