from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Vehiculo
from .forms import VehiculoForm

def vehiculos_dashboard(request):
    vehiculos = Vehiculo.objects.all()
    form = VehiculoForm()

    if request.method == "POST":
        if 'vehiculo_submit' in request.POST:
            form = VehiculoForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Vehículo creado correctamente.")
                return redirect('vehiculos_dashboard')

        elif 'vehiculo_update' in request.POST:
            vehiculo_id = request.POST.get('vehiculo_id')
            vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)
            form = VehiculoForm(request.POST, instance=vehiculo)
            if form.is_valid():
                form.save()
                messages.success(request, "Vehículo actualizado correctamente.")
                return redirect('vehiculos_dashboard')

    context = {
        'vehiculos': vehiculos,
        'form': form,
    }
    return render(request, "vehiculos/vehiculos_dashboard.html", context)
