from django.urls import path
from . import views

app_name = "creditos"

urlpatterns = [
    path("nuevo/", views.crear_credito, name="crear_credito"), # type: ignore

    path("items/<int:credito_id>/", views.popover_items_credito, name="popover_items_credito"), # type: ignore
    
    path("cancelar/<int:credito_id>/", views.cancelar_credito, name="cancelar_credito"),

]
