from django.urls import path
from . import views

urlpatterns = [
    path('', views.almacen_dashboard, name='almacen_dashboard'),
    path("productos/editar/<int:id>/", views.editar_producto, name="editar_producto"),
]
