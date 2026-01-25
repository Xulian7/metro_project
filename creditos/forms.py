from django import forms
from .models import Credito, CreditoItem
from arrendamientos.models import Contrato


class CreditoForm(forms.ModelForm):
    """
    Formulario principal del crédito (cabecera).
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
        fields = ["contrato", "tipo", "descripcion"]
        widgets = {
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Comentario opcional…"
            }),
        }

class CreditoItemForm(forms.ModelForm):
    """
    Formulario base para un item de crédito.
    Se reutiliza para almacén / taller / efectivo.
    """

    class Meta:
        model = CreditoItem
        fields = [
            "descripcion",
            "cantidad",
            "valor_unitario",
            "subtotal",
        ]
        widgets = {
            "descripcion": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "cantidad": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1
            }),
            "valor_unitario": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01"
            }),
            "subtotal": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "readonly": True
            }),
        }
