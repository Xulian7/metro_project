from django.http import JsonResponse
from vehiculos.models import Vehiculo
from arrendamientos.models import Contrato
from clientes.models import Cliente


def get_datos_vehiculo(request):
    placa = request.GET.get('placa', '').strip()

    try:
        # 1️⃣ Buscar el vehículo por placa
        vehiculo = Vehiculo.objects.get(placa=placa)

        # 2️⃣ Buscar contrato asociado al vehículo
        contrato = Contrato.objects.filter(vehiculo_id=vehiculo.id).first()
        if not contrato:
            return JsonResponse({'error': 'Contrato no encontrado para este vehículo'})

        # 3️⃣ Buscar el cliente del contrato
        cliente = Cliente.objects.get(id=contrato.cliente_id)

        data = {
            'cedula': cliente.cedula,
            'cliente': cliente.nombre,     # ajusta si tu campo se llama diferente
        }

        return JsonResponse(data)

    except Vehiculo.DoesNotExist:
        return JsonResponse({'error': 'Vehículo no encontrado'})
    except Cliente.DoesNotExist:
        return JsonResponse({'error': 'Cliente no encontrado'})
