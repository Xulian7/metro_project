from django.urls import path
from . import views

app_name = "terminal_pagos"

urlpatterns = [
    path("facturar/", views.crear_factura, name="crear_factura"),
]
