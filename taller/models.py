from django.db import models

class Servicio(models.Model):
    nombre_servicio = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre_servicio


class Mecanico(models.Model):
    nombre = models.CharField(max_length=100)
    identificacion = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre
