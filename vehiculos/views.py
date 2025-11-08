from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from .models import Vehiculo
from .forms import VehiculoForm

# ==========================================================
# DASHBOARD PRINCIPAL (listar y crear vehículos)
# ==========================================================
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

    context = {
        'vehiculos': vehiculos,
        'form': form,
    }
    return render(request, "vehiculos/vehiculos_dashboard.html", context)


# ==========================================================
# ACTUALIZAR VEHÍCULO (AJAX)
# ==========================================================
def vehiculo_update(request):
    if request.method == 'POST':
        vehiculo_id = request.POST.get('vehiculo_id')
        if not vehiculo_id:
            return HttpResponseBadRequest('Falta el ID del vehículo.')

        vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)

        # Actualizar campos
        vehiculo.placa = request.POST.get('placa')
        vehiculo.marca = request.POST.get('marca')
        vehiculo.modelo = request.POST.get('modelo')
        vehiculo.serie = request.POST.get('serie')
        vehiculo.propietario = request.POST.get('propietario')
        vehiculo.numero_motor = request.POST.get('numero_motor')
        vehiculo.numero_chasis = request.POST.get('numero_chasis')
        vehiculo.linea_gps = request.POST.get('linea_gps')  # 🛰️ nuevo campo
        vehiculo.actualizacion_soat = request.POST.get('actualizacion_soat')
        vehiculo.estado = request.POST.get('estado')
        vehiculo.save()

        # Devolver JSON para que el front actualice la tabla sin recargar
        return JsonResponse({
            'status': 'ok',
            'vehiculo': {
                'id': vehiculo.id,
                'placa': vehiculo.placa,
                'marca': vehiculo.marca,
                'modelo': vehiculo.modelo,
                'serie': vehiculo.serie,
                'propietario': vehiculo.propietario,
                'numero_motor': vehiculo.numero_motor,
                'numero_chasis': vehiculo.numero_chasis,
                'linea_gps': vehiculo.linea_gps,  # 🛰️ devuelto al frontend
                'actualizacion_soat': vehiculo.actualizacion_soat,
                'estado': vehiculo.estado,
            }
        })

    return HttpResponseBadRequest('Método no permitido.')
