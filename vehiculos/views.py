from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Vehiculo
from .forms import VehiculoForm

def vehiculos_dashboard(request):
    form = VehiculoForm()
    return render(request, "vehiculos/vehiculos_dashboard.html", {"form": form})

def vehiculos_tabla(request):
    # Obtener filtros
    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '')
    propietario = request.GET.get('propietario', '')

    vehiculos = Vehiculo.objects.all().order_by('placa')
    if q:
        vehiculos = vehiculos.filter(
            placa__icontains=q
        ) | vehiculos.filter(
            marca__icontains=q
        ) | vehiculos.filter(
            modelo__icontains=q
        )
    if estado:
        vehiculos = vehiculos.filter(estado=estado)
    if propietario:
        vehiculos = vehiculos.filter(propietario__icontains=propietario)

    # Paginación
    paginator = Paginator(vehiculos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Si es HTMX, renderizamos solo la tabla
    if request.headers.get('HX-Request'):
        return render(request, "vehiculos/vehiculos_tabla_partial.html", {"page_obj": page_obj})

    return render(request, "vehiculos/vehiculos_dashboard.html", {"page_obj": page_obj, "form": VehiculoForm()})

def vehiculo_crear_actualizar(request):
    if request.method == "POST":
        vehiculo_id = request.POST.get('vehiculo_id')
        if vehiculo_id:
            vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)
            form = VehiculoForm(request.POST, instance=vehiculo)
        else:
            form = VehiculoForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Vehículo guardado correctamente.")
        else:
            messages.error(request, "Hubo un error con los datos.")
    return redirect('vehiculos_tabla')

