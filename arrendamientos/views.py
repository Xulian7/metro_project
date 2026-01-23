from django.shortcuts import render, redirect, get_object_or_404
from .models import Contrato
from .forms import ContratoForm
from django.http import JsonResponse
from vehiculos.models import Vehiculo
from clientes.models import Cliente
from django.views.decorators.http import require_POST
from django.contrib import messages

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


    if request.method == 'POST':
        print("Form is_valid antes de commit:", form.is_valid())
        print("🔥 Form errors antes de commit:", form.errors)

        if form.is_valid():
            # Guardar sin enviar estado en el POST
            contrato = form.save(commit=False)
            contrato.estado = 'Activo'  # Se asigna automáticamente
            contrato.save()

            # Cambiar el estado del vehículo a Activo
            vehiculo = contrato.vehiculo
            vehiculo.estado = 'Activo'
            vehiculo.save()
            messages.success(request, "Contrato creado correctamente.")
            
            return redirect('arrendamientos:contratos')

    return render(request, 'arrendamientos/contratos.html', {
        'form': form,
        'contratos': contratos
    })


@require_POST
def actualizar_contrato(request, contrato_id):
    contrato = get_object_or_404(Contrato, id=contrato_id)
    nuevo_estado = request.POST.get("estado")
    vehiculo = contrato.vehiculo

    # 🛑 VALIDACIÓN CLAVE
    if contrato.estado == "Inactivo" and nuevo_estado == "Activo":
        existe_otro_activo = Contrato.objects.filter(
            vehiculo=vehiculo,
            estado="Activo"
        ).exclude(id=contrato.id).exists() # type: ignore

        if existe_otro_activo:
            messages.error(
                request,
                f"La placa {vehiculo} ya tiene un contrato activo."
            )
            return redirect('arrendamientos:contratos')

    # 🔹 Actualización normal
    contrato.fecha_inicio = request.POST.get("fecha_inicio")
    contrato.tarifa = request.POST.get("tarifa")
    contrato.frecuencia_pago = request.POST.get("frecuencia_pago")  # 👈 NUEVO
    contrato.dias_contrato = request.POST.get("dias_contrato")
    contrato.visitador = request.POST.get("visitador")
    contrato.estado = nuevo_estado

    if nuevo_estado == "Inactivo":
        contrato.motivo = request.POST.get("motivo")
        vehiculo.estado = "Vitrina"
    else:
        contrato.motivo = None
        vehiculo.estado = "Activo"

    contrato.save()
    vehiculo.save()

    messages.success(request, "Contrato actualizado correctamente.")
    return redirect('arrendamientos:contratos')





def reportes(request):
    return render(request, 'arrendamientos/reportes.html')


