from django.db import models
from django.contrib.auth.models import User

class Vehiculo(models.Model):
    ESTADO_CHOICES = [
        ('Activo', 'Activo'),
        ('Vitrina', 'Vitrina'),
        ('Inactivo', 'Inactivo'),
    ]

    ESTADO_OBS_CHOICES = [
        ('Transito/Policia', 'Tránsito / Policía'),
        ('Hurto', 'Hurto'),
        ('Siniestro', 'Siniestro'),
        ('Traspaso Permanente', 'Traspaso Permanente'),
        ('Otros', 'Otros'),
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
    linea_gps = models.CharField(max_length=50, blank=True, null=True)
    estado_obs = models.CharField(
        max_length=30,
        choices=ESTADO_OBS_CHOICES,
        blank=True,
        null=True,
        help_text="Observación del estado solo si el vehículo está inactivo."
    )

    def __str__(self):
        return f"{self.placa}"

    @property
    def cliente_actual(self):
        return None
