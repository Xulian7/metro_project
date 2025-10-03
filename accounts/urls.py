from django.urls import path
from .views import MyLoginView, MyLogoutView, home

urlpatterns = [
    path('', home, name='home'),
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
]
