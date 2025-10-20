from django.urls import path
from . import views

#urlpatterns = [
#    path('', views.clientes_view, name='clientes_view'),
#]

urlpatterns = [
    path('clientes/', views.clientes_view, name='clientes'),
    path('clientes/<int:pk>/', views.clientes_view, name='editar_cliente'),
]
