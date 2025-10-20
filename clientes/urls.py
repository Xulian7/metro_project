from django.urls import path
from . import views

urlpatterns = [
    path('', views.clientes_view, name='clientes_view'),
]
