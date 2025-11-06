from django.urls import path
from . import views

urlpatterns = [
    path('', views.clientes_dashboard, name='clientes_dashboard'),
    path('update/', views.cliente_update, name='cliente_update'),
]

