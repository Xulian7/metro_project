from django.urls import path
from .views import terminal_pagos_view

urlpatterns = [
    path('', terminal_pagos_view, name='terminal_pagos'),
]
