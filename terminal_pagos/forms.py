from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from arrendamientos.models import Contrato


class MedioPago(models.Model):
    """
    Catálogo de medios de pago (Efectivo, Nequi, Daviplata, Tarjeta, etc)
    """
    nombre = models.CharField(max_length=50, unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Factura(models.Model):
    """
    Factura principal asociada a un contrato (placa + cliente viven allí)
    """
    contrato = models.ForeignKey(
        Contrato,
        on_delete=models.PROTECT,
        related_name="facturas"
    )

    fecha = models.DateTimeField(auto_now_add=True)

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0)]
    )

    observaciones = models.TextField(blank=True, null=True)

    cerrada = models.BooleanField(
        default=False,
        help_text="Una factura cerrada no puede modificarse"
    )

    def __str__(self):
        return f"Factura #{self.id} - {self.contrato}"

    def recalcular_total(self):
        total = sum(
            item.total for item in self.items.all()
        )
        self.total = total
        self.save(update_fields=["total"])


class ItemFactura(models.Model):
    """
    Ítems que componen una factura.
    Pueden ser tarifas, productos, servicios o pagos especiales.
    """

    TIPO_ITEM = [
        ("TARIFA", "Tarifa"),
        ("PRODUCTO", "Producto Almacén"),
        ("TALLER", "Servicio Taller"),
        ("ESPECIAL", "Pago Especial"),
    ]

    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        related_name="items"
    )

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_ITEM
    )

    descripcion = models.CharField(max_length=255)

    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("1.00"),
        validators=[MinValueValidator(0)]
    )

    valor_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0)]
    )

    # Campos opcionales según tipo
    producto_id = models.IntegerField(
        blank=True,
        null=True,
        help_text="ID del producto del almacén (si aplica)"
    )

    servicio_id = models.IntegerField(
        blank=True,
        null=True,
        help_text="ID del servicio de taller (si aplica)"
    )

    def save(self, *args, **kwargs):
        self.total = self.cantidad * self.valor_unitario
        super().save(*args, **kwargs)
        self.factura.recalcular_total()

    def __str__(self):
        return f"{self.tipo} - {self.descripcion}"


class PagoFactura(models.Model):
    """
    Permite pagar una factura con múltiples medios de pago
    (ej: parte efectivo, parte Nequi)
    """

    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        related_name="pagos"
    )

    medio_pago = models.ForeignKey(
        MedioPago,
        on_delete=models.PROTECT
    )

    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    referencia = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Referencia del pago (voucher, transacción, etc)"
    )

    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medio_pago} - {self.valor}"
