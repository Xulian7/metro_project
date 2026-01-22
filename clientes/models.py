from django.db import models
from django.contrib.auth.models import User

class Cliente(models.Model):
    TIPO_CHOICES = [
        ('Normal', 'Normal'),
        ('Inversionista', 'Inversionista'),
    ]

    STATUS_CHOICES = [
        ('Normal', 'Normal'),
        ('Lista Negra', 'Lista Negra'),
    ]

    cedula = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    nacionalidad = models.CharField(max_length=50, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    referencia_1 = models.CharField(max_length=100, blank=True, null=True)
    telefono_ref_1 = models.CharField(max_length=20, blank=True, null=True)
    referencia_2 = models.CharField(max_length=100, blank=True, null=True)
    telefono_ref_2 = models.CharField(max_length=20, blank=True, null=True)

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='Normal'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Normal',
        blank=True,
        null=True
    )

    # 👇 NUEVOS CAMPOS (solo para Inversionista)
    costo_operativo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )

    costo_administrativo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.nombre
