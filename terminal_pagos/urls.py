from django.urls import path
from . import views

app_name = "terminal_pagos"

urlpatterns = [
    path("", views.nueva_transaccion, name="nueva_transaccion"),
    path("facturar/", views.crear_factura, name="crear_factura"),
]
