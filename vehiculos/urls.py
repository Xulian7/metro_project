from django.urls import path
from . import views

urlpatterns = [
    path('', views.vehiculos_dashboard, name='vehiculos_dashboard'),
    path('update/', views.vehiculo_update, name='vehiculo_update'),
    path("catalogo/", views.catalogo_marcas, name="catalogo_marcas"),
    path("cargar-series/", views.cargar_series, name="cargar_series"),
 
]