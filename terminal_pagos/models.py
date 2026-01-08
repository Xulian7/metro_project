from django.db import models
from arrendamientos.models import Contrato


# =========================
# FACTURA
# =========================
class Factura(models.Model):
    ESTADOS = (
        ("borrador", "Borrador"),
        ("confirmada", "Confirmada"),
        ("anulada", "Anulada"),
    )

    ESTADOS_PAGO = (
        ("pendiente", "Pendiente"),
        ("parcial", "Parcial"),
        ("pagada", "Pagada"),
    )

    contrato = models.ForeignKey(
        Contrato,
        on_delete=models.PROTECT,
        related_name="facturas"
    )

    fecha = models.DateTimeField(auto_now_add=True)

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="borrador"
    )

    estado_pago = models.CharField(
        max_length=20,
        choices=ESTADOS_PAGO,
        default="pendiente"
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    total_pagado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return f"Factura #{self.id} - {self.fecha.date()}"


# =========================
# ITEMS DE FACTURA
# =========================
class ItemFactura(models.Model):
    TIPOS_ITEM = (
        ("tarifa", "Tarifa"),
        ("otro", "Otro pago"),
        ("almacen", "Ítem de almacén"),
        ("taller", "Servicio de taller"),
    )

    factura = models.ForeignKey(
        Factura,
        related_name="items",
        on_delete=models.CASCADE
    )

    tipo_item = models.CharField(
        max_length=20,
        choices=TIPOS_ITEM
    )

    descripcion = models.CharField(
        max_length=255,
        blank=True
    )

    cantidad = models.PositiveIntegerField(
        default=1
    )

    valor_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    producto_almacen = models.ForeignKey(
        "almacen.Producto",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    servicio_taller = models.ForeignKey(
        "taller.Servicio",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.get_tipo_item_display()} - {self.subtotal}"


# =========================
# CATÁLOGO DE CUENTAS
# =========================
class Cuenta(models.Model):
    nombre = models.CharField(
        max_length=50,
        unique=True
    )

    activa = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.nombre


# =========================
# CATÁLOGO DE TIPOS DE PAGO
# =========================
class TipoPago(models.Model):
    codigo = models.CharField(
        max_length=30,
        unique=True
    )

    nombre = models.CharField(
        max_length=50
    )

    requiere_origen = models.BooleanField(
        default=False
    )

    requiere_referencia = models.BooleanField(
        default=False
    )

    es_egreso = models.BooleanField(
        default=False
    )

    activo = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.nombre


# =========================
# PAGOS DE FACTURA
# =========================
class PagoFactura(models.Model):

    factura = models.ForeignKey(
        Factura,
        related_name="pagos",
        on_delete=models.CASCADE
    )

    tipo_pago = models.ForeignKey(
        TipoPago,
        on_delete=models.PROTECT
    )

    cuenta = models.ForeignKey(
        Cuenta,
        on_delete=models.PROTECT
    )

    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    origen = models.CharField(
        max_length=50,
        blank=True
    )

    referencia = models.CharField(
        max_length=100,
        blank=True
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.tipo_pago} | {self.cuenta} | {self.valor}"
