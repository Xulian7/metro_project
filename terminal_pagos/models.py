from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator


# =========================
# FACTURA
# =========================
class Factura(models.Model):

    ESTADOS = (
        ("ABIERTA", "Abierta"),
        ("PAGADA", "Pagada"),
        ("ANULADA", "Anulada"),
    )

    contrato = models.ForeignKey(
        "arrendamientos.Contrato",
        on_delete=models.PROTECT,
        related_name="facturas"
    )

    consecutivo = models.CharField(max_length=20, unique=True)
    fecha = models.DateTimeField(default=timezone.now)

    estado = models.CharField(
        max_length=10,
        choices=ESTADOS,
        default="ABIERTA"
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return f"Factura {self.consecutivo}"

    @property
    def total_pagado(self):
        return self.pagos.aggregate(
            total=models.Sum("valor")
        )["total"] or 0

    @property
    def saldo(self):
        return self.total - self.total_pagado


# =========================
# ITEMS DE FACTURA
# =========================
class ItemFactura(models.Model):

    TIPOS = (
        ("TARIFA", "Tarifa"),
        ("PRODUCTO", "Producto"),
        ("TALLER", "Servicio de Taller"),
        ("ESPECIAL", "Pago Especial"),
    )

    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        related_name="items"
    )

    tipo = models.CharField(
        max_length=10,
        choices=TIPOS
    )

    descripcion = models.CharField(max_length=255)

    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1,
        validators=[MinValueValidator(0)]
    )

    valor_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False
    )

    # Relaciones opcionales según tipo
    producto = models.ForeignKey(
        "almacen.Producto",
        null=True,
        blank=True,
        on_delete=models.PROTECT
    )

    servicio_taller = models.ForeignKey(
        "taller.Servicio",
        null=True,
        blank=True,
        on_delete=models.PROTECT
    )

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.valor_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tipo} - {self.descripcion}"


# =========================
# MEDIOS DE PAGO
# =========================
class MedioPago(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


# =========================
# PAGOS A FACTURA
# =========================
class PagoFactura(models.Model):
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
        null=True
    )

    fecha = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.medio_pago} - {self.valor}"
