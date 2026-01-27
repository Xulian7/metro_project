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
    color = models.CharField(max_length=50, blank=True, null=True)
    propietario = models.CharField(max_length=100)
    numero_motor = models.CharField(max_length=50, blank=True, null=True)
    numero_chasis = models.CharField(max_length=50, blank=True, null=True)
    actualizacion_soat = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='Vitrina')
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
    
    def save(self, *args, **kwargs):
        if self.placa:
            self.placa = self.placa.strip().upper()
        super().save(*args, **kwargs)


    @property
    def cliente_actual(self):
        return None


class Marca(models.Model):
    nombre = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='series',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Marca / Serie"
        verbose_name_plural = "Marcas y Series"
        ordering = ["parent__id", "nombre"]

    def __str__(self):
        if self.parent:
            return f"{self.parent.nombre} → {self.nombre}"
        return self.nombre

    @property
    def es_marca(self):
        return self.parent is None

    @property
    def es_serie(self):
        return self.parent is not None
