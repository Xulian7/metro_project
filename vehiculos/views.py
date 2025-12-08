from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from .models import Vehiculo
from .forms import VehiculoForm
from clientes.models import Cliente
from .models import Marca
from .forms import MarcaForm
from datetime import datetime

# ==========================================================
# DASHBOARD PRINCIPAL (listar y crear vehículos)
# ==========================================================
def vehiculos_dashboard(request):
    vehiculos = Vehiculo.objects.all().order_by('placa')
    form = VehiculoForm()
    inversionistas = Cliente.objects.filter(tipo="Inversionista").order_by("nombre")

    # ===========================
    # AÑADIDO: catálogo de marcas
    # ===========================
    marcas = Marca.objects.filter(parent__isnull=True).order_by("nombre")

    # ===========================
    # AÑADIDO: años de modelo
    # ===========================
    year_now = datetime.now().year
    modelos = list(range(2018, year_now + 2))  # 2010 → año actual + 1

    if request.method == "POST":
        # ========================
        # CREAR NUEVO VEHÍCULO
        # ========================
        if 'vehiculo_submit' in request.POST:
            form = VehiculoForm(request.POST)
            if form.is_valid():
                vehiculo = form.save(commit=False)
                vehiculo.estado = "Vitrina"
                vehiculo.estado_obs = None
                vehiculo.save()

                messages.success(request, "🚗 Vehículo creado correctamente.")
                return redirect('vehiculos_dashboard')
            else:
                messages.error(request, "⚠️ Revisa los datos del formulario.")

    context = {
        'vehiculos': vehiculos,
        'form': form,
        'inversionistas': inversionistas,

        # → NUEVO
        'marcas': marcas,
        'modelos': modelos,
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
        vehiculo.linea_gps = request.POST.get('linea_gps')
        vehiculo.actualizacion_soat = request.POST.get('actualizacion_soat')
        vehiculo.estado = request.POST.get('estado')
        vehiculo.estado_obs = request.POST.get('estado_obs')
        vehiculo.save()

        # Devolver JSON para actualizar fila
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
                'linea_gps': vehiculo.linea_gps,
                'actualizacion_soat': str(vehiculo.actualizacion_soat),
                'estado': vehiculo.estado,
                'estado_obs': vehiculo.estado_obs,
            }
        })

    return HttpResponseBadRequest('Método no permitido.')

# ==========================================================
# CATÁLOGO DE MARCAS Y SERIES
# ==========================================================
def catalogo_marcas(request):
    marcas = Marca.objects.filter(parent__isnull=True)
    series = Marca.objects.filter(parent__isnull=False)

    form = MarcaForm()

    if request.method == "POST":
        form = MarcaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✔ Registro guardado correctamente.")
            return redirect("catalogo_marcas")
        else:
            messages.error(request, "⚠ Hay errores en el formulario.")

    context = {
        "form": form,
        "marcas": marcas,
        "series": series,
    }
    return render(request, "vehiculos/catalogo_marcas.html", context)



def cargar_series(request):
    marca_id = request.GET.get("marca_id")

    if not marca_id:
        return JsonResponse({"series": []})

    series = Marca.objects.filter(parent_id=marca_id).order_by("nombre")

    data = [{"id": s.id, "nombre": s.nombre} for s in series]

    return JsonResponse({"series": data})