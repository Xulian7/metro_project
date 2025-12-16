from django.urls import path
from . import views

app_name = 'arrendamientos'

urlpatterns = [
    path('lista_cobros/', views.lista_cobros, name='lista_cobros'),
    path('contratos/', views.contratos, name='contratos'),
    path('reportes/', views.reportes, name='reportes'),
    path('contratos/update/<int:contrato_id>/', views.actualizar_contrato, name='update_contrato'),
    path('ajax/get-cedula/', views.get_cedula_cliente, name='get_cedula_cliente'),

]
