# urls.py
from django.urls import path
from .views import MyLoginView, MyLogoutView, home, vehiculos_vitrina

urlpatterns = [
    # Página principal con slider de vehículos en vitrina
    path('', vehiculos_vitrina, name='home'),

    # Login / Logout
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', MyLogoutView.as_view(), name='logout'),


]
