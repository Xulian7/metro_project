from django.db import models
from django.contrib.auth.models import User

class Vehiculo(models.Model):
    ESTADO_CHOICES = [
        ('Activo', 'Activo'),
        ('Vitrina', 'Vitrina'),
        ('Inactivo', 'Inactivo'),
    ]

    placa = models.CharField(max_length=20, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    serie = models.CharField(max_length=50, blank=True, null=True)
    propietario = models.CharField(max_length=100)
    numero_motor = models.CharField(max_length=50, blank=True, null=True)
    numero_chasis = models.CharField(max_length=50, blank=True, null=True)
    actualizacion_soat = models.DateField()
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='Activo')

    def __str__(self):
        return f"{self.placa} - {self.marca} {self.modelo}"
    
    # 🔹 Placeholder para la relación futura con contratos
    @property
    def cliente_actual(self):
        return None
