from django.contrib import admin
from .models import CierreCaja, CierreCajaDetalle

class CierreCajaDetalleInline(admin.TabularInline):
    model = CierreCajaDetalle
    extra = 0
    readonly_fields = ("medio", "total_sistema", "diferencia")

@admin.register(CierreCaja)
class CierreCajaAdmin(admin.ModelAdmin):
    list_display = (
        "operador",
        "fecha_inicio",
        "fecha_fin",
        "total_sistema",
        "total_arqueo",
        "diferencia",
        "autorizado",
    )
    list_filter = ("autorizado", "operador")
    inlines = [CierreCajaDetalleInline]
