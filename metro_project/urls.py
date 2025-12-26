"""
URL configuration for metro_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from accounts.views import MyLoginView, MyLogoutView, home
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', home, name='home'),
    # Login y logout nativos de Django
    path("accounts/login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path('almacen/', include('almacen.urls')),
    path('vehiculos/', include('vehiculos.urls')),
    path('clientes/', include('clientes.urls')),
    path('arrendamientos/', include('arrendamientos.urls')),
    path('taller/', include('taller.urls')),
    path('terminal-pagos/', include('terminal_pagos.urls')),
    
]

