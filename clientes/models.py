from django.db import models

class Cliente(models.Model):
    TIPO_CHOICES = [
        ('normal', 'Normal'),
        ('inversionista', 'Inversionista'),
    ]

    STATUS_CHOICES = [
        ('normal', 'Normal'),
        ('lista_negra', 'Lista Negra'),
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
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='normal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='normal', blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.cedula})"
