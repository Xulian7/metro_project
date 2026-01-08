from django.shortcuts import render, redirect, get_object_or_404
from .models import Factura
from .forms import FacturaForm, ItemFacturaFormSet
from almacen.models import Producto
from taller.models import Servicio
from .models import Cuenta, TipoPago
from .forms import CuentaForm, TipoPagoForm
from django.utils import timezone
from terminal_pagos.models import TipoPago, Cuenta


def nueva_transaccion(request):
    productos = Producto.objects.values("id", "nombre", "precio_venta")
    servicios = Servicio.objects.values("id", "nombre_servicio", "valor")
    

    factura_form = FacturaForm()
    item_formset = ItemFacturaFormSet()

    return render(request, "terminal_pagos/terminal_pagos.html", {
        "factura_form": factura_form,
        "item_formset": item_formset,
        "productos_json": list(productos),
        "servicios_json": list(servicios),
    })


from django.utils import timezone
from terminal_pagos.models import TipoPago, Cuenta


def crear_factura(request):
    if request.method == "POST":
        factura_form = FacturaForm(request.POST)
        factura = Factura()

        item_formset = ItemFacturaFormSet(
            request.POST,
            instance=factura
        )

        if factura_form.is_valid() and item_formset.is_valid():
            factura = factura_form.save()
            item_formset.instance = factura
            item_formset.save()

            return redirect("terminal_pagos:crear_factura")

    else:
        factura_form = FacturaForm()
        item_formset = ItemFacturaFormSet()

    # 🔹 NUEVO: catálogos de pagos
    tipos_pago = TipoPago.objects.filter(activo=True)
    cuentas = Cuenta.objects.filter(activa=True)

    context = {
        "factura_form": factura_form,
        "item_formset": item_formset,

        # 🔽 no interfiere con nada existente
        "tipos_pago": tipos_pago,
        "cuentas": cuentas,
        "today": timezone.now().date(),
    }

    return render(
        request,
        "terminal_pagos/crear_factura.html",
        context
    )




# catalogo de pagos/views.py
def catalogos_pago(request):
    cuenta_id = request.GET.get("cuenta")
    tipo_id = request.GET.get("tipo")

    cuenta_instance = Cuenta.objects.filter(id=cuenta_id).first()
    tipo_instance = TipoPago.objects.filter(id=tipo_id).first()

    cuenta_form = CuentaForm(
        request.POST or None,
        instance=cuenta_instance,
        prefix="cuenta"
    )

    tipo_form = TipoPagoForm(
        request.POST or None,
        instance=tipo_instance,
        prefix="tipo"
    )

    if request.method == "POST":
        if "guardar_cuenta" in request.POST and cuenta_form.is_valid():
            cuenta_form.save()
            return redirect("terminal_pagos:catalogos_pago")

        if "guardar_tipo" in request.POST and tipo_form.is_valid():
            tipo_form.save()
            return redirect("terminal_pagos:catalogos_pago")

    return render(request, "terminal_pagos/catalogos_pago.html", {
        "cuentas": Cuenta.objects.all(),
        "tipos": TipoPago.objects.all(),
        "cuenta_form": cuenta_form,
        "tipo_form": tipo_form,
    })

