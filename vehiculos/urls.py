from django.urls import path
from . import views

urlpatterns = [
    path('', views.vehiculos_dashboard, name='vehiculos_dashboard'),
]

