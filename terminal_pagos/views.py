from django.shortcuts import render, redirect
from django.db import transaction
from .forms import FacturaForm
from .models import Factura, DetalleFactura, Pago
from vehiculos.models import Vehiculo
from arrendamientos.models import Contrato
from django.http import JsonResponse   # ← necesario para la nueva vista


def terminal_pagos_view(request):

    if request.method == 'POST':
        form = FacturaForm(request.POST)
        # 👇 NO tocamos nada del guardado
        if form.is_valid():
            try:
                with transaction.atomic():
                    factura = form.save(commit=False)
                    factura.save()

                    items_nombres = request.POST.getlist('item_nombre[]')
                    items_cantidades = request.POST.getlist('item_cantidad[]')
                    items_valores = request.POST.getlist('item_valor[]')

                    for nombre, cantidad, valor in zip(items_nombres, items_cantidades, items_valores):
                        if nombre.strip():
                            DetalleFactura.objects.create(
                                factura=factura,
                                descripcion=nombre,
                                cantidad=int(cantidad),
                                valor_unitario=float(valor)
                            )

                    pagos_tipos = request.POST.getlist('pago_tipo[]')
                    pagos_valores = request.POST.getlist('pago_valor[]')

                    for tipo, valor in zip(pagos_tipos, pagos_valores):
                        if tipo.strip() and valor.strip():
                            Pago.objects.create(
                                factura=factura,
                                tipo=tipo,
                                valor=float(valor)
                            )

                return redirect('terminal_pagos')

            except Exception as e:
                form.add_error(None, f"Ocurrió un error al guardar la factura: {str(e)}")

    else:
        form = FacturaForm()

    # 🆕 NUEVO: traer placas de ambas tablas
    vehiculos_ids = Contrato.objects.values_list("vehiculo_id", flat=True)
    placas = Vehiculo.objects.filter(id__in=vehiculos_ids).values_list("placa", flat=True)

    # Quitar duplicados y ordenar
    placas = sorted(set(placas))

    return render(request, 'terminal_pagos/terminal.html', {
        'form': form,
        'placas': placas,  # ← IMPORTANTE
    })


# ========================================
# 🚀 NUEVA VISTA AJAX PARA AUTORELLENAR
# ========================================
def get_datos_vehiculo(request):
    placa = request.GET.get("placa")

    if not placa:
        return JsonResponse({"error": "Placa no enviada"}, status=400)

    try:
        # 1. Buscar vehículo
        vehiculo = Vehiculo.objects.get(placa=placa)

        # 2. Buscar el contrato más reciente de ese vehículo
        contrato = (
            Contrato.objects.filter(vehiculo_id=vehiculo.id)
            .order_by("-id")
            .first()
        )

        if not contrato:
            return JsonResponse({"error": "Este vehículo no tiene contrato registrado"}, status=404)

        # 3. Cliente asociado
        cliente = contrato.cliente

        return JsonResponse({
            "cedula": cliente.cedula,
            "nombre": cliente.nombre,
        })

    except Vehiculo.DoesNotExist:
        return JsonResponse({"error": "Vehículo no encontrado"}, status=404)

    except Exception as e:
        return JsonResponse({"error": f"Error interno: {str(e)}"}, status=500)
