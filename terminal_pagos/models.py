from django.db import models


class Factura(models.Model):
    ESTADOS = (
        ("borrador", "Borrador"),
        ("confirmada", "Confirmada"),
        ("anulada", "Anulada"),
    )

    placa = models.CharField(max_length=20, blank=True, null=True)
    nombre_cliente = models.CharField(max_length=150, blank=True, null=True)

    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="borrador")

    total = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )  # calculado luego

    def __str__(self):
        return f"Factura #{self.id} - {self.fecha.date()}"


class ItemFactura(models.Model):
    TIPOS_ITEM = (
        ("tarifa", "Tarifa"),
        ("otro", "Otro pago"),
        ("almacen", "Ítem de almacén"),
        ("taller", "Servicio de taller"),
    )

    factura = models.ForeignKey(
        Factura, related_name="items", on_delete=models.CASCADE
    )

    tipo_item = models.CharField(max_length=20, choices=TIPOS_ITEM)

    descripcion = models.CharField(max_length=255, blank=True)
    cantidad = models.PositiveIntegerField(default=1)
    valor_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    # Referencias opcionales
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


class PagoFactura(models.Model):
    MEDIOS_PAGO = (
        ("efectivo", "Efectivo"),
        ("tarjeta", "Tarjeta"),
        ("nequi", "Nequi"),
        ("otro", "Otro"),
    )

    factura = models.ForeignKey(
        Factura, related_name="pagos", on_delete=models.CASCADE
    )

    medio_pago = models.CharField(max_length=20, choices=MEDIOS_PAGO)
    valor = models.DecimalField(max_digits=12, decimal_places=2)

    referencia = models.CharField(max_length=100, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_medio_pago_display()} - {self.valor}"

