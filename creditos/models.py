from django.db import models
from arrendamientos.models import Contrato


class Credito(models.Model):
    """
    Representa una deuda adicional asociada a un contrato.
    NO es un pago, NO es una factura.
    """

    TIPO_CHOICES = [
        ("almacen", "Artículo de almacén"),
        ("taller", "Servicio de taller"),
        ("efectivo", "Préstamo de efectivo"),
    ]

    ESTADO_CHOICES = [
        ("Activo", "Activo"),
        ("Cancelado", "Cancelado"),
    ]

    contrato = models.ForeignKey(
        Contrato,
        on_delete=models.PROTECT,
        related_name="creditos",
        help_text="Contrato al que se asocia el crédito"
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        help_text="Tipo de crédito"
    )

    descripcion = models.TextField(
        blank=True,
        help_text="Comentario general del crédito (opcional)"
    )

    monto_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Valor total del crédito"
    )

    saldo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Saldo pendiente del crédito"
    )

    fecha = models.DateField(
        auto_now_add=True,
        help_text="Fecha de creación del crédito"
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="Activo"
    )

    class Meta:
        ordering = ["-fecha", "-id"]
        verbose_name = "Crédito"
        verbose_name_plural = "Créditos"

    def __str__(self):
        return f"Crédito #{self.id} - {self.contrato}" # type: ignore

    def puede_eliminarse(self):
        """
        Regla de negocio:
        Un crédito solo puede eliminarse si NO tiene pagos asociados.
        (El modelo de pagos vendrá después)
        """
        return not hasattr(self, "pagos") or self.pagos.count() == 0 # type: ignore


class CreditoItem(models.Model):
    """
    Detalle de un crédito.
    Puede representar:
    - un artículo de almacén
    - un servicio de taller
    - un préstamo en efectivo (1 solo item)
    """

    credito = models.ForeignKey(
        Credito,
        on_delete=models.CASCADE,
        related_name="items"
    )

    descripcion = models.CharField(
        max_length=255,
        help_text="Descripción del item"
    )

    cantidad = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Cantidad (solo aplica para almacén o taller)"
    )

    valor_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valor unitario (solo aplica para almacén o taller)"
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Subtotal del item"
    )

    class Meta:
        verbose_name = "Ítem de crédito"
        verbose_name_plural = "Ítems de crédito"

    def __str__(self):
        return f"{self.descripcion} - ${self.subtotal}"
