from django import forms
from django.forms import inlineformset_factory
from .models import Factura, ItemFactura
from arrendamientos.models import Contrato

class ContratoSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(
            name, value, label, selected, index, subindex=subindex, attrs=attrs
        )

        if value:
            try:
                contrato = Contrato.objects.get(pk=value)
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


