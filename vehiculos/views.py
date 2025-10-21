from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Vehiculo
from .forms import VehiculoForm

def vehiculos_dashboard(request):
    vehiculos = Vehiculo.objects.all().order_by('placa')
    form = VehiculoForm()

    if request.method == "POST":
        # ========================
        # CREAR NUEVO VEHÍCULO
        # ========================
        if 'vehiculo_submit' in request.POST:
            form = VehiculoForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "🚗 Vehículo creado correctamente.")
                return redirect('vehiculos_dashboard')
            else:
                messages.error(request, "⚠️ Revisa los datos del formulario.")

        # ========================
        # ACTUALIZAR VEHÍCULO EXISTENTE
        # ========================
        elif 'vehiculo_update' in request.POST:
            vehiculo_id = request.POST.get('vehiculo_id')

            if not vehiculo_id:
                messages.error(request, "No se encontró el vehículo a actualizar.")
                return redirect('vehiculos_dashboard')

            vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)
            form = VehiculoForm(request.POST, instance=vehiculo)
            if form.is_valid():
                form.save()
                messages.success(request, f"🛠️ Vehículo {vehiculo.placa} actualizado correctamente.")
                return redirect('vehiculos_dashboard')
            else:
                messages.error(request, "⚠️ No se pudo actualizar el vehículo. Verifica los datos.")

    context = {
        'vehiculos': vehiculos,
        'form': form,
    }
    return render(request, "vehiculos/vehiculos_dashboard.html", context)
