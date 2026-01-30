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
    hoy = now().date()

    soat_data = []
    tecno_data = []

    for v in Vehiculo.objects.all():

        # ================================
        # 🚑 SOAT
        # ================================
        if v.actualizacion_soat:
            fecha_vencimiento_soat = v.actualizacion_soat + timedelta(days=365)
            dias_soat = (fecha_vencimiento_soat - hoy).days
        else:
            dias_soat = None

        soat_data.append({
            "placa": v.placa,
            "dias": dias_soat
        })

        # ================================
        # 🔧 TECNOMECÁNICA
        # ================================
        if v.tecnomecanica:
            dias_tecno = (v.tecnomecanica - hoy).days
        else:
            dias_tecno = None

        tecno_data.append({
            "placa": v.placa,
            "dias": dias_tecno
        })

    # Ordenar: el que vence primero arriba
    soat_data.sort(key=lambda x: x["dias"] if x["dias"] is not None else 99999)
    tecno_data.sort(key=lambda x: x["dias"] if x["dias"] is not None else 99999)

    return render(request, 'accounts/home.html', {
        'user': request.user,
        'vehiculos': vehiculos,
        'soat_data': soat_data,
        'tecno_data': tecno_data
    })

