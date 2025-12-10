from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.timezone import now
from vehiculos.models import Vehiculo
from datetime import timedelta


class MyLoginView(LoginView):
    template_name = 'accounts/login.html'


class MyLogoutView(LogoutView):
    next_page = '/login/'


@login_required
def home(request):
    vehiculos = Vehiculo.objects.filter(estado='Vitrina')

    # ================================
    # 🔥 Cálculo del widget SOAT
    # ================================
    hoy = now().date()
    soat_data = []

    for v in Vehiculo.objects.all():

        if v.actualizacion_soat:
            fecha_vencimiento = v.actualizacion_soat + timedelta(days=365)
            dias = (fecha_vencimiento - hoy).days
        else:
            dias = None  # Sin fecha → sin cálculo

        soat_data.append({
            "placa": v.placa,
            "dias": dias
        })

    # Ordenamos del que vence más pronto al que falta más
    soat_data = sorted(
        soat_data,
        key=lambda x: x["dias"] if x["dias"] is not None else 99999
    )

    return render(request, 'accounts/home.html', {
        'user': request.user,
        'vehiculos': vehiculos,
        'soat_data': soat_data  # 👉 Se envía al template
    })
