from django.contrib import admin
from .models import Factura, DetalleFactura, Pago


class DetalleFacturaInline(admin.TabularInline):
    model = DetalleFactura
    extra = 1
    readonly_fields = ('subtotal',)
    fields = ('item_n', 'concepto', 'descripcion', 'valor_unitario', 'cantidad', 'subtotal')


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1
    fields = ('medio_pago', 'origen_nequi', 'valor', 'referencia', 'fecha_pago')
    readonly_fields = ('fecha_pago',)


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'cliente', 'cedula', 'placa', 'total_factura', 'saldo_pendiente', 'cerrada', 'fecha_creacion')
    list_filter = ('cerrada', 'fecha_creacion')
    search_fields = ('numero', 'cliente', 'cedula', 'placa')
    readonly_fields = ('fecha_creacion', 'total_factura', 'saldo_pendiente', 'cerrada')
    inlines = [DetalleFacturaInline, PagoInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.actualizar_totales()


@admin.register(DetalleFactura)
class DetalleFacturaAdmin(admin.ModelAdmin):
    list_display = ('factura', 'item_n', 'concepto', 'descripcion', 'valor_unitario', 'cantidad', 'subtotal')
    list_filter = ('concepto',)
    search_fields = ('factura__numero', 'descripcion')


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('factura', 'medio_pago', 'origen_nequi', 'valor', 'referencia', 'fecha_pago')
    list_filter = ('medio_pago', 'origen_nequi')
    search_fields = ('factura__numero', 'referencia')
