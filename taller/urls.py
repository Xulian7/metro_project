from django.urls import path
from .views import taller_panel

urlpatterns = [
    path('', taller_panel, name='taller_panel'),
]
