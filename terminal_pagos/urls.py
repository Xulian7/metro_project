from django.urls import path
from . import views

app_name = "terminal_pagos"

urlpatterns = [
    path("", views.nueva_transaccion, name="nueva_transaccion"),
    path("facturar/", views.crear_factura, name="crear_factura"),
    path("catalogos-pago/", views.catalogos_pago, name="catalogos_pago"),
    path("medios-pago/", views.medios_pago, name="medios_pago"),
    path("validar-medio/<int:config_id>/", views.validar_pago, name="validar_medio"),
    
]
