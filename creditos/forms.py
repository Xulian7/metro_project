from django import forms
from .models import Credito
from arrendamientos.models import Contrato


class CreditoForm(forms.ModelForm):
    """
    Formulario de cabecera del crédito.
    Un crédito puede tener múltiples items de distintos tipos.
    """

    contrato = forms.ModelChoiceField(
        queryset=Contrato.objects.filter(estado="Activo"),
        label="Contrato",
        widget=forms.Select(attrs={
            "class": "form-select"
        })
    )

    class Meta:
        model = Credito
        fields = ["contrato", "descripcion"]
        widgets = {
            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Comentario general del crédito (opcional)…"
            }),
        }
