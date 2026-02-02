from django.db import models
from django.contrib.auth.models import User

class CierreCaja(models.Model):
    operador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="cierres_caja"
    )

    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()

    total_sistema = models.DecimalField(max_digits=12, decimal_places=2)
    total_arqueo = models.DecimalField(max_digits=12, decimal_places=2)
    diferencia = models.DecimalField(max_digits=12, decimal_places=2)

    autorizado = models.BooleanField(default=False)

    observacion = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_fin"]

    def __str__(self):
        return f"Cierre {self.operador.username} {self.fecha_fin.date()}"



class CierreCajaDetalle(models.Model):
    cierre = models.ForeignKey(
        CierreCaja,
        on_delete=models.CASCADE,
        related_name="detalles"
    )

    medio = models.CharField(max_length=50)
    cuenta = models.CharField(max_length=100)

    total_sistema = models.DecimalField(max_digits=12, decimal_places=2)
    total_arqueo = models.DecimalField(max_digits=12, decimal_places=2)
    diferencia = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.medio} - {self.cuenta}"
