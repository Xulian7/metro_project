from django.http import JsonResponse
from vehiculos.models import Vehiculo
from arrendamientos.models import Contrato
from clientes.models import Cliente

def get_datos_vehiculo(request):
    placa = request.GET.get('placa')

    try:
        vehiculo = Vehiculo.objects.get(placa=placa)
    except Vehiculo.DoesNotExist:
        return JsonResponse({"error": "Vehículo no encontrado"})

    contrato = Contrato.objects.filter(vehiculo=vehiculo).first()
    if not contrato:
        return JsonResponse({"error": "No hay contrato asociado a este vehículo"})

    cliente = Cliente.objects.get(id=contrato.cliente_id)

    return JsonResponse({
        "cedula": cliente.cedula,
        "cliente": cliente.nombre
    })
