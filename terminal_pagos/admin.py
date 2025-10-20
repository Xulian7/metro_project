from django.contrib import admin
from .models import Transaccion

@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tipo_pago', 'valor', 'medio_pago', 'origen', 'fecha_ingreso')
    list_filter = ('tipo_pago', 'medio_pago', 'origen')
    search_fields = ('cliente', 'placa', 'cedula', 'referencia')
