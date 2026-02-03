from django.urls import path
from . import views

app_name = "reportes"

urlpatterns = [
    path("cierres/nuevo/", views.nuevo_cierre, name="nuevo_cierre"),
    path(
        "cierres/<int:cierre_id>/",
        views.detalle_cierre,
        name="detalle_cierre"
    ),
    
    path(
        "dashboard/",
        views.dashboard_reportes,
        name="dashboard_reportes"
    ),
]
