from django.http import JsonResponse
from vehiculos.models import Vehiculo

def get_datos_vehiculo(request):
    placa = request.GET.get("placa", "").strip()

    if not placa:
        return JsonResponse({"error": "No se envió la placa."}, status=400)

    try:
        vehiculo = Vehiculo.objects.get(placa=placa)
    except Vehiculo.DoesNotExist:
        return JsonResponse({"error": "Vehículo no encontrado."}, status=404)

    cliente = vehiculo.cliente_actual  # ← magia negra Django-style

    if not cliente:
        return JsonResponse({"error": "El vehículo no tiene contrato activo."}, status=404)

    return JsonResponse({
        "cedula": cliente.cedula,
        "cliente": cliente.nombre
    })
