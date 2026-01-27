from django.urls import path
from . import views

app_name = "creditos"

urlpatterns = [
    # Crear + listar créditos (misma pantalla)
    path("nuevo/", views.crear_credito, name="crear_credito"), # type: ignore

    # Endpoint AJAX → items de un crédito (popover)
    path("items/<int:credito_id>/", views.credito_items, name="credito_items"),
]