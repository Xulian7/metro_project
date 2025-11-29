from django.shortcuts import render, redirect, get_object_or_404
from .models import Servicio, Mecanico
from .forms import ServicioForm, MecanicoForm

def taller_panel(request):
    # Formularios vacíos para crear
    servicio_form = ServicioForm()
    mecanico_form = MecanicoForm()

    # Crear servicio
    if request.method == "POST" and "crear_servicio" in request.POST:
        servicio_form = ServicioForm(request.POST)
        if servicio_form.is_valid():
            servicio_form.save()
            return redirect('taller_panel')

    # Crear mecánico
    if request.method == "POST" and "crear_mecanico" in request.POST:
        mecanico_form = MecanicoForm(request.POST)
        if mecanico_form.is_valid():
            mecanico_form.save()
            return redirect('taller_panel')

    # Editar servicio
    if request.method == "POST" and "editar_servicio" in request.POST:
        servicio = get_object_or_404(Servicio, id=request.POST.get("id_edit"))
        form_edit = ServicioForm(request.POST, instance=servicio)
        if form_edit.is_valid():
            form_edit.save()
            return redirect('taller_panel')

    # Editar mecánico
    if request.method == "POST" and "editar_mecanico" in request.POST:
        mecanico = get_object_or_404(Mecanico, id=request.POST.get("id_edit"))
        form_edit = MecanicoForm(request.POST, instance=mecanico)
        if form_edit.is_valid():
            form_edit.save()
            return redirect('taller_panel')

    # Eliminar servicio
    if request.method == "POST" and "eliminar_servicio" in request.POST:
        Servicio.objects.filter(id=request.POST.get("id_delete")).delete()
        return redirect('taller_panel')

    # Eliminar mecánico
    if request.method == "POST" and "eliminar_mecanico" in request.POST:
        Mecanico.objects.filter(id=request.POST.get("id_delete")).delete()
        return redirect('taller_panel')

    context = {
        "servicio_form": servicio_form,
        "mecanico_form": mecanico_form,
        "servicios": Servicio.objects.all(),
        "mecanicos": Mecanico.objects.all(),
    }

    return render(request, "taller/panel.html", context)
