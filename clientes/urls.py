from django.urls import path
from . import views

urlpatterns = [
    path('', views.clientes_dashboard, name='vehiculos_dashboard'),
    path('update/', views.cliente_update, name='vehiculo_update'),
]
