from django.db import models

class Transaccion(models.Model):
    TIPOS_PAGO = [
        ('arrendamientos', 'Tarifa Arrendamientos'),
        ('pago_inicial', 'Pago Inicial Contrato'),
        ('compra_almacen', 'Compra Almacén - Taller'),
        ('pago_empeños', 'Pago Empeños'),
        ('otros', 'Otros Pagos'),
    ]

    MEDIOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('nequi', 'Nequi'),
        ('ajuste_pp', 'Ajuste P/P'),
        ('comision', 'Comisión'),
    ]

    ORIGEN_NEQUI = [
        ('nequi_directo', 'Nequi directo'),
        ('consignacion', 'Consignación'),
        ('bancolombia', 'Bancolombia'),
        ('transfiya', 'Transfiya'),
        ('ptm', 'PTM'),
    ]

    tipo_pago = models.CharField(max_length=30, choices=TIPOS_PAGO)
    placa = models.CharField(max_length=20)
    cedula = models.CharField(max_length=20)
    cliente = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    medio_pago = models.CharField(max_length=20, choices=MEDIOS_PAGO)
    origen = models.CharField(max_length=20, choices=ORIGEN_NEQUI, blank=True, null=True)
    referencia = models.CharField(max_length=50, blank=True)
    fecha_ingreso = models.DateTimeField()  # editable por el usuario

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.medio_pago == 'nequi' and not self.origen:
            raise ValidationError({'origen': 'Debe seleccionar un origen si el medio de pago es Nequi.'})

    def __str__(self):
        return f"{self.cliente} - {self.tipo_pago} - {self.valor}"
