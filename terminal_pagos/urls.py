from django.urls import path
from . import views

app_name = "terminal_pagos"

urlpatterns = [
    path("", views.nueva_transaccion, name="nueva_transaccion"),
    path("facturar/", views.crear_factura, name="crear_factura"),
    path("catalogos-pago/", views.catalogos_pago, name="catalogos_pago"),
    path("medios-pago/", views.medios_pago, name="medios_pago"),
    path("validar-medio/<int:pago_id>/", views.validar_pago, name="validar_medio"),
    path("resumen-contratos/", views.resumen_contratos, name="resumen_contratos"),
    path("extracto/contrato/<int:contrato_id>/", views.extracto_contrato, name="extracto_contrato"),
    path("extracto/factura/<int:factura_id>/", views.detalle_factura_pagos, name="detalle_factura_pagos"),
    path("validar-referencia/", views.validar_referencia_pago, name="validar_referencia_pago"),
    path("visor-facturas/", views.visor_facturas, name="visor_facturas"),
    path("visor-facturas/detalle/<int:factura_id>/", views.detalle_factura_json, name="detalle_factura_json"),

    # ANULACIÓN DE FACTURA
    path(
        "facturas/anular/<int:factura_id>/",
        views.anular_factura,
        name="anular_factura"
    ),
]
