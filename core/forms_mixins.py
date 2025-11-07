from django import forms
from django.core.exceptions import ValidationError

class SmartCleanMixin(forms.ModelForm):
    """
    Mixin global para limpiar campos de forma inteligente:
    - Los campos numéricos solo aceptan dígitos o valores válidos de tipo numérico.
    - Los campos de texto se formatean a Nombre Propio (Title Case).
    """

    def clean(self):
        cleaned_data = super().clean()
        model = self._meta.model

        for field_name, value in cleaned_data.items():
            if value in (None, ''):
                continue  # Ignorar campos vacíos

            model_field = model._meta.get_field(field_name)
            internal_type = model_field.get_internal_type()

            # 🔢 Validar campos numéricos
            if internal_type in [
                'IntegerField', 'PositiveIntegerField', 'BigIntegerField',
                'SmallIntegerField', 'FloatField', 'DecimalField'
            ]:
                if isinstance(value, str):
                    try:
                        float(value.replace(',', '.'))
                    except ValueError:
                        raise ValidationError(
                            {field_name: f"El campo '{model_field.verbose_name}' solo acepta números."}
                        )

            # 🧠 Convertir campos de texto a Nombre Propio
            elif internal_type in ['CharField', 'TextField'] and isinstance(value, str):
                # Limpieza de espacios y formato
                value = " ".join(value.strip().split()).title()
                cleaned_data[field_name] = value

        return cleaned_data

