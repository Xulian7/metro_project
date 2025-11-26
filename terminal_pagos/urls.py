from django.urls import path
from .views import terminal_pagos_view, get_datos_vehiculo

urlpatterns = [
    path('', terminal_pagos_view, name="terminal_pagos"),
    path('get-datos', get_datos_vehiculo, name="get_datos_vehiculo"),
]
