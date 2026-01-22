from django.db import models
from clientes.models import Cliente
from vehiculos.models import Vehiculo

class Contrato(models.Model):

    TIPO_CONTRATO_CHOICES = [
        ('opcion_compra', 'Opción de compra'),
        ('alquiler', 'Alquiler'),
    ]

    FRECUENCIA_PAGO_CHOICES = [
        ('diario', 'Diario'),
        ('semanal', 'Semanal'),
        ('quincenal', 'Quincenal'),
        ('mensual', 'Mensual'),
    ]

    MOTIVO_INACTIVO_CHOICES = [
        ('Finalizado', 'Finalizado'),
        ('Cancelado', 'Cancelado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.PROTECT,
        limit_choices_to={'estado': 'Vitrina'}
    )

    fecha_inicio = models.DateField()

    cuota_inicial = models.DecimalField(max_digits=12, decimal_places=2)
    tarifa = models.DecimalField(max_digits=12, decimal_places=2)

    # ⬇️ ESTE CAMPO SE VUELVE DERIVADO, NO SEMÁNTICO
    dias_contrato = models.PositiveIntegerField(
        help_text="Duración total del contrato en días"
    )

    frecuencia_pago = models.CharField(
        max_length=20,
        choices=FRECUENCIA_PAGO_CHOICES,
        default='mensual',
        help_text="Frecuencia con la que se generan cobros"
    )

    visitador = models.CharField(max_length=100)

    tipo_contrato = models.CharField(
        max_length=20,
        choices=TIPO_CONTRATO_CHOICES
    )

    estado = models.CharField(
        max_length=20,
        default='Activo'
    )

    motivo = models.CharField(
        max_length=20,
        choices=MOTIVO_INACTIVO_CHOICES,
        blank=True,
        null=True,
        help_text="Motivo del estado inactivo del contrato."
    )

    def __str__(self):
        return f"{self.cliente.nombre} - {self.vehiculo.placa}"
