from django.urls import path
from . import views

urlpatterns = [
    path('', views.vehiculos_dashboard, name='vehiculos_dashboard'),
    path('tabla/', views.vehiculos_tabla, name='vehiculos_tabla'),
    path('guardar/', views.vehiculo_crear_actualizar, name='vehiculo_guardar'),
]
