from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

class MyLoginView(LoginView):
    template_name = 'accounts/login.html'

class MyLogoutView(LogoutView):
    next_page = '/login/'

@login_required
def home(request):
    return render(request, 'accounts/home.html', {'user': request.user})

