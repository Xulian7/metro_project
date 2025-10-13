from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Vehiculo
from .forms import VehiculoForm

def vehiculos_dashboard(request):
    vehiculos = Vehiculo.objects.all().order_by('placa')

    # ---------------------------
    # Filtros avanzados
    # ---------------------------
    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '')
    propietario = request.GET.get('propietario', '')

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

    # ---------------------------
    # Paginación
    # ---------------------------
    paginator = Paginator(vehiculos, 10)  # 10 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # ---------------------------
    # Formularios
    # ---------------------------
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
        'page_obj': page_obj,
        'form': form,
        'q': q,
        'estado': estado,
        'propietario': propietario,
    }
    return render(request, 'vehiculos/vehiculos_dashboard.html', context)
