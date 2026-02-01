from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
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

    # Campo mantenido por compatibilidad / UI
    # Idealmente se recalcula desde servicios
    estado_pago = models.CharField(
        max_length=20,
        choices=ESTADOS_PAGO,
        default="pendiente"
    )

    total = models.DecimalField(
    max_digits=12,
    decimal_places=2,
    default=Decimal("0.00")
    )

    total_pagado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="facturas_creadas",
        null=True,
        blank=True
    )

    # ===== Metadatos de anulación =====
    anulada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="facturas_anuladas",
        null=True,
        blank=True
    )

    fecha_anulacion = models.DateTimeField(
        null=True,
        blank=True
    )

    motivo_anulacion = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"Factura #{self.id}" # type: ignore


# =========================
# ITEMS DE FACTURA
# =========================
class ItemFactura(models.Model):
    TIPOS_ITEM = (
        ("tarifa", "Tarifa"),
        ("multa", "Pago de multa"),
        ("otro", "Otro pago"),
        ("almacen", "Ítem de almacén"),
        ("abono_credito", "Abono a crédito"),
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

    cantidad = models.PositiveIntegerField(default=1)

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

    credito = models.ForeignKey(
        "creditos.Credito",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="items_factura"
    )

    def __str__(self):
        return f"{self.get_tipo_item_display()} - {self.subtotal}" # type: ignore


# =========================
# CUENTAS DESTINO
# =========================
class Cuenta(models.Model):
    nombre = models.CharField(
        max_length=50,
        unique=True
    )

    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


# =========================
# MEDIOS DE PAGO
# =========================
class MedioPago(models.Model):
    nombre = models.CharField(
        max_length=50,
        unique=True
    )

    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


# =========================
# CANALES DE PAGO
# =========================
class CanalPago(models.Model):
    medio = models.ForeignKey(
        MedioPago,
        on_delete=models.CASCADE,
        related_name="canales"
    )

    nombre = models.CharField(max_length=50)

    requiere_referencia = models.BooleanField(default=False)

    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ("medio", "nombre")

    def __str__(self):
        return f"{self.medio} - {self.nombre}"


# =========================
# CONFIGURACIÓN DE PAGO
# =========================
class ConfiguracionPago(models.Model):
    medio = models.ForeignKey(
        MedioPago,
        on_delete=models.CASCADE,
        related_name="configuraciones"
    )

    cuenta_destino = models.ForeignKey(
        Cuenta,
        on_delete=models.PROTECT,
        related_name="configuraciones"
    )

    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ("medio", "cuenta_destino")
        verbose_name = "Configuración de pago"
        verbose_name_plural = "Configuraciones de pago"

    def __str__(self):
        return f"{self.medio} → {self.cuenta_destino}"


# =========================
# PAGOS DE FACTURA
# =========================
class PagoFactura(models.Model):
    factura = models.ForeignKey(
        Factura,
        related_name="pagos",
        on_delete=models.CASCADE
    )

    configuracion = models.ForeignKey(
        ConfiguracionPago,
        on_delete=models.PROTECT,
        related_name="pagos"
    )

    canal = models.ForeignKey(
        CanalPago,
        on_delete=models.PROTECT,
        related_name="pagos"
    )

    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    # Referencia ACTUAL (puede mutar al anular)
    referencia = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    # Referencia ORIGINAL (nunca cambia)
    referencia_original = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True
    )

    fecha_pago = models.DateField(default=timezone.now)

    validado = models.BooleanField(default=False)

    # Marca pagos negativos por compensación
    es_compensacion = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Captura automática de la referencia original
        if self.referencia and not self.referencia_original:
            self.referencia_original = self.referencia
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Factura {self.factura_id} | {self.valor}" # type: ignore
