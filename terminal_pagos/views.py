from django.shortcuts import render, redirect
from django.db import transaction
from .forms import FacturaForm
from .models import Factura, DetalleFactura, Pago
from django.http import JsonResponse
from arrendamientos.models import Contrato
from vehiculos.models import Vehiculo
from clientes.models import Cliente

def terminal_pagos_view(request):
    """
    Vista principal del módulo de pagos.
    Permite registrar una nueva factura con sus ítems y pagos asociados,
    y listar las facturas más recientes.
    """
    if request.method == 'POST':
        form = FacturaForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    # 🧾 Guardar la factura principal
                    factura = form.save(commit=False)
                    factura.save()

                    # 🧮 Procesar los ítems de la factura
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

                    # 💰 Procesar los pagos asociados
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

    # 📋 Listamos las 10 facturas más recientes
    facturas = Factura.objects.order_by('-fecha_creacion')[:10]

    return render(request, 'terminal_pagos/terminal.html', {
        'form': form,
        'facturas': facturas
    })

def get_info_por_placa(request, vehiculo_id):
    try:
        contrato = Contrato.objects.select_related(
            "cliente", "vehiculo"
        ).get(vehiculo_id=vehiculo_id)

        return JsonResponse({
            "ok": True,
            "cedula": contrato.cliente.cedula,
            "cliente_nombre": contrato.cliente.nombre,
        })

    except Contrato.DoesNotExist:
        return JsonResponse({"ok": False})