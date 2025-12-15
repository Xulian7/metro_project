from django.shortcuts import render, redirect, get_object_or_404
from .models import Contrato
from .forms import ContratoForm
from django.http import JsonResponse
from vehiculos.models import Vehiculo
from clientes.models import Cliente

def get_cedula_cliente(request):
    cliente_id = request.GET.get('cliente_id')

    if not cliente_id:
        return JsonResponse({'error': 'Cliente no enviado'}, status=400)

    try:
        cliente = Cliente.objects.get(id=cliente_id)
        return JsonResponse({'cedula': cliente.cedula})
    except Cliente.DoesNotExist:
        return JsonResponse({'error': 'Cliente no encontrado'}, status=404)


def lista_cobros(request):
    return render(request, 'arrendamientos/lista_cobros.html')


def contratos(request):
    contratos = Contrato.objects.all()
    form = ContratoForm(request.POST or None)

    print("🔥 Método:", request.method)
    print("🔥 POST data:", request.POST)

    if request.method == 'POST':
        print("🔥 Form is_valid antes de commit:", form.is_valid())
        print("🔥 Form errors antes de commit:", form.errors)

        if form.is_valid():
            # Guardar sin enviar estado en el POST
            contrato = form.save(commit=False)
            contrato.estado = 'Activo'  # Se asigna automáticamente
            contrato.save()
            print("🔥 Contrato guardado con estado:", contrato.estado)

            # Cambiar el estado del vehículo a Activo
            vehiculo = contrato.vehiculo
            vehiculo.estado = 'Activo'
            vehiculo.save()
            print("🔥 Vehículo actualizado a estado:", vehiculo.estado)

            return redirect('arrendamientos:contratos')

    return render(request, 'arrendamientos/contratos.html', {
        'form': form,
        'contratos': contratos
    })


# 🔥 NUEVA VIEW PARA EDITAR DESDE EL MODAL
def update_contrato(request, contrato_id):
    contrato = get_object_or_404(Contrato, id=contrato_id)

    if request.method == "POST":
        estado = request.POST.get("estado")
        motivo = request.POST.get("motivo")

        # Validación: si estado = Inactivo → motivo obligatorio
        if estado == "Inactivo" and not motivo:
            return JsonResponse({"error": "Debe seleccionar un motivo."}, status=400)

        contrato.estado = estado
        contrato.motivo = motivo if estado == "Inactivo" else None
        contrato.save()

        return JsonResponse({"success": True})

    return JsonResponse({"error": "Método no permitido"}, status=405)


def reportes(request):
    return render(request, 'arrendamientos/reportes.html')
