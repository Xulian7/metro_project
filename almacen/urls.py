from django.urls import path
from . import views

urlpatterns = [
    path('', views.almacen_dashboard, name='almacen_dashboard'),
]
