from django.urls import path
from .views import terminal_pagos

urlpatterns = [
    path('', terminal_pagos, name='terminal_pagos'),
]
