from django.db import models
from clientes.models import Cliente
from vehiculos.models import Vehiculo

class Contrato(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT, limit_choices_to={'estado': 'Inactivo'})
    fecha_inicio = models.DateField()
    cuota_inicial = models.DecimalField(max_digits=12, decimal_places=2)
    tarifa = models.DecimalField(max_digits=12, decimal_places=2)
    dias_contrato = models.PositiveIntegerField()
    visitador = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, default='Activo')

    def __str__(self):
        return f"{self.cliente.nombre} - {self.vehiculo.placa}"
