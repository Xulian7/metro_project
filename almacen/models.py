from django.db import models

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    nit = models.CharField(max_length=50, unique=True)
    telefono = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    referencia = models.CharField(max_length=100, unique=True)
    utilidad = models.CharField(max_length=100, blank=True, null=True)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    ean = models.CharField(max_length=13, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.referencia})"


class Movimiento(models.Model):
    TIPO_MOVIMIENTO = [
        ('ingreso_compra', 'Compra a proveedor'),
        ('ingreso_devolucion_cliente', 'Devolución cliente'),
        ('ingreso_ajuste', 'Ajuste ingreso'),
        ('salida_devolucion_proveedor', 'Devolución a proveedor'),
        ('salida_cortesia', 'Cortesía'),
        ('salida_ajuste', 'Ajuste salida'),
        ('salida_venta', 'Venta'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=30, choices=TIPO_MOVIMIENTO)
    cantidad = models.IntegerField()
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateField(auto_now_add=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    factura_referencia = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Factura o documento relacionado (proveedor, cliente, placa, etc.)"
    )

    def __str__(self):
        ref = f" - Ref: {self.factura_referencia}" if self.factura_referencia else ""
        return f"{self.producto.nombre} - {self.tipo} - {self.cantidad}{ref}"

    def valor_total(self):
        return self.cantidad * self.precio_unitario

