from django import forms
from django.forms import inlineformset_factory
from .models import Factura, ItemFactura
from arrendamientos.models import Contrato
from .models import Cuenta, TipoPago

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


# pagos/forms.py
class CuentaForm(forms.ModelForm):
    class Meta:
        model = Cuenta
        fields = ["nombre", "activa"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "activa": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class TipoPagoForm(forms.ModelForm):
    class Meta:
        model = TipoPago
        fields = [
            "codigo",
            "nombre",
            "requiere_origen",
            "requiere_referencia",
            "es_egreso",
            "activo",
        ]
        widgets = {
            "codigo": forms.TextInput(attrs={"class": "form-control"}),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
        }
