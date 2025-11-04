from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models.signals import post_delete
from django.dispatch import receiver


class Factura(models.Model):
    """
    Representa una factura general que agrupa varios ítems (productos o servicios)
    y los pagos aplicados a ellos.
    """
    numero = models.AutoField(primary_key=True)
    cedula = models.CharField(max_length=20)
    placa = models.CharField(max_length=20, blank=True, null=True)
    cliente = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    total_factura = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo_pendiente = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cerrada = models.BooleanField(default=False)

    def __str__(self):
        return f"Factura #{self.numero} - {self.cliente} ({self.cedula})"

    def actualizar_totales(self):
        """
        Recalcula el total de la factura y su saldo pendiente.
        """
        total = sum([item.subtotal for item in self.detallefactura_set.all()])
        pagos = sum([p.valor for p in self.pago_set.all()])
        self.total_factura = total
        self.saldo_pendiente = total - pagos
        self.cerrada = self.saldo_pendiente <= 0
        self.save()


class DetalleFactura(models.Model):
    """
    Representa cada ítem de una factura (producto, servicio, tarifa, abono, etc.)
    """
    CONCEPTOS = [
        ('almacen', 'Compra Almacén - Taller'),
        ('servicio_taller', 'Servicio Taller'),
        ('deuda_adicional', 'Deuda Adicional'),
        ('arrendamiento', 'Tarifa Arrendamiento'),
        ('empeno', 'Pago Empeño'),
        ('abono_inicial', 'Abono a Inicial'),
    ]

    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    item_n = models.PositiveIntegerField(blank=True, null=True)
    concepto = models.CharField(max_length=30, choices=CONCEPTOS)
    descripcion = models.CharField(max_length=200, blank=True)
    valor_unitario = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    cantidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def clean(self):
        # Solo permitir un "Abono a Inicial" por factura
        if self.concepto == 'abono_inicial':
            existe = DetalleFactura.objects.filter(
                factura=self.factura,
                concepto='abono_inicial'
            ).exclude(pk=self.pk).exists()
            if existe:
                raise ValidationError('Ya existe un abono inicial en esta factura.')

    def save(self, *args, **kwargs):
        # Numeración automática de ítems
        if not self.item_n:
            ultimo = DetalleFactura.objects.filter(factura=self.factura).aggregate(models.Max('item_n'))['item_n__max']
            self.item_n = (ultimo or 0) + 1

        # Calcular subtotal
        self.subtotal = self.valor_unitario * self.cantidad

        super().save(*args, **kwargs)
        self.factura.actualizar_totales()

    def __str__(self):
        return f"Factura {self.factura.numero} - Ítem {self.item_n} ({self.get_concepto_display()})"


class Pago(models.Model):
    """
    Registra los pagos asociados a una factura, con detalle del medio utilizado.
    """
    MEDIOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('nequi', 'Nequi'),
        ('ajuste_pp', 'Ajuste Pico y Placa'),
        ('comision', 'Comisión'),
    ]

    ORIGEN_NEQUI = [
        ('transf_nequi', 'Transf Nequi'),
        ('bancolombia', 'Bancolombia'),
        ('consignacion', 'Consignación'),
        ('ptm', 'PTM'),
        ('transfiya', 'TransfiYa'),
    ]

    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    medio_pago = models.CharField(max_length=20, choices=MEDIOS_PAGO)
    origen_nequi = models.CharField(max_length=20, choices=ORIGEN_NEQUI, blank=True, null=True)
    valor = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    referencia = models.CharField(max_length=50, blank=True, null=True)

    def clean(self):
        if self.medio_pago == 'nequi' and not self.origen_nequi:
            raise ValidationError({'origen_nequi': 'Debe especificar el origen si el medio es Nequi.'})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.factura.actualizar_totales()

    def __str__(self):
        return f"Pago {self.valor} - {self.get_medio_pago_display()} (Factura {self.factura.numero})"


# 🔁 Señales para recalcular totales al eliminar un ítem o un pago
@receiver(post_delete, sender=DetalleFactura)
@receiver(post_delete, sender=Pago)
def actualizar_totales_post_delete(sender, instance, **kwargs):
    instance.factura.actualizar_totales()
