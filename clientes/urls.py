from django.urls import path
from . import views

urlpatterns = [
    path('', views.clientes_dashboard, name='clientes_dashboard'),
    path('update/', views.clientes_update, name='clientes_update'),
    path('<int:pk>/get/', views.cliente_get, name='cliente_get'),  # Para el modal
]

