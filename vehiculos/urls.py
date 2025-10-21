from django.urls import path
from . import views

urlpatterns = [
    path('', views.vehiculos_dashboard, name='vehiculos_dashboard'),
    path('vehiculos/update/', views.vehiculo_update, name='vehiculo_update'),

]

