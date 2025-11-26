from django.urls import path
from . import views

urlpatterns = [
    path('pagos/', views.terminal_pagos_view, name='terminal_pagos'),
]
