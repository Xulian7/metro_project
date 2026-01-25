from django.urls import path
from . import views

app_name = "creditos"

urlpatterns = [
    path("nuevo/", views.crear_credito, name="crear_credito"),
]
