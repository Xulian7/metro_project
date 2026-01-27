from time import timezone
from django.db import models
from arrendamientos.models import Contrato
from django.utils import timezone

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
        default=0 # type: ignore
    )

    total_pagado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0 # type: ignore
    )

    def __str__(self):
        return f"Factura #{self.id} - {self.fecha.date()}" # type: ignore


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
# (pertenecen al medio)
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
# MEDIO → CUENTA
# (los canales se heredan)
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

    referencia = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )
    
    def save(self, *args, **kwargs):
        if not self.referencia:
            self.referencia = None
        super().save(*args, **kwargs)

    fecha_pago = models.DateField(default=timezone.now)
    
    validado = models.BooleanField(default=False)


    
    def __str__(self):
        return (
            f"Factura {self.factura_id} | " # type: ignore
            f"{self.configuracion.medio} - {self.canal.nombre} | "
            f"{self.valor}"
        )

