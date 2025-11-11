from django.shortcuts import render, redirect
from .models import Contrato
from .forms import ContratoForm
from vehiculos.models import Vehiculo

def lista_cobros(request):
    return render(request, 'arrendamientos/lista_cobros.html')

def contratos(request):
    contratos = Contrato.objects.all()
    form = ContratoForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        contrato = form.save()

        # Cambiar el estado del vehículo a Activo
        vehiculo = contrato.vehiculo
        vehiculo.estado = 'Activo'
        vehiculo.save()

        return redirect('arrendamientos:contratos')

    return render(request, 'arrendamientos/contratos.html', {'form': form, 'contratos': contratos})

def reportes(request):
    return render(request, 'arrendamientos/reportes.html')
