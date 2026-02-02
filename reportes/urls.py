from django.urls import path
from . import views

app_name = "reportes"

urlpatterns = [
    path("cierres/nuevo/", views.nuevo_cierre, name="nuevo_cierre"),
]
