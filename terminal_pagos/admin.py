from django.contrib import admin
from .models import Factura, ItemFactura, PagoFactura


class ItemFacturaInline(admin.TabularInline):
    model = ItemFactura
    extra = 0


class PagoFacturaInline(admin.TabularInline):
    model = PagoFactura
    extra = 0


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    inlines = [ItemFacturaInline, PagoFacturaInline]
    list_display = ("id", "fecha", "estado", "total")


admin.site.register(ItemFactura)
admin.site.register(PagoFactura)
