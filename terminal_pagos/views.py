from django.shortcuts import render, redirect
from django.db import transaction
from .forms import FacturaForm
from .models import Factura, DetalleFactura, Pago
from vehiculos.models import Vehiculo
from arrendamientos.models import Contrato


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
    placas_vehiculos = Vehiculo.objects.values_list("placa", flat=True)
    vehiculos_ids = Contrato.objects.values_list("vehiculo_id", flat=True)
    placas_contratos = Vehiculo.objects.filter(id__in=vehiculos_ids).values_list("placa", flat=True)

    # Quitar duplicados y ordenar
    placas = sorted(set(placas_vehiculos) | set(placas_contratos))

    # Listado de facturas recientes (no lo usamos pero lo dejo igual)
    facturas = Factura.objects.order_by('-fecha_creacion')[:10]

    return render(request, 'terminal_pagos/terminal.html', {
        'form': form,
        'facturas': facturas,
        'placas': placas,  # ← IMPORTANTE
    })
