from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now

from .models import (
    Factura,
    Cuenta,
    OrigenFondo,
    CanalPago,
    OrigenCanal,
    PagoFactura,
)

from .forms import (
    FacturaForm,
    ItemFacturaFormSet,
    CuentaForm,
    OrigenFondoForm,
    CanalPagoForm,
    OrigenCanalForm,
    PagoFacturaForm,
)

from almacen.models import Producto
from taller.models import Servicio


# =========================
# TERMINAL DE PAGOS
# =========================
def nueva_transaccion(request):
    # -------------------------
    # CATÁLOGOS PARA JS (JSON)
    # -------------------------
    productos = Producto.objects.values(
        "id",
        "nombre",
        "precio_venta"
    )

    servicios = Servicio.objects.values(
        "id",
        "nombre_servicio",
        "valor"
    )

    origenes_canales = OrigenCanal.objects.select_related(
        "origen",
        "canal"
    ).filter(
        activo=True,
        origen__activo=True,
        canal__activo=True
    ).values(
        "id",
        "origen__nombre",
        "canal__nombre",
        "canal__requiere_referencia",
        "canal__es_egreso",
    )

    cuentas = Cuenta.objects.filter(
        activa=True
    ).values(
        "id",
        "nombre"
    )

    # -------------------------
    # FORMS
    # -------------------------
    factura_form = FacturaForm()
    item_formset = ItemFacturaFormSet()

    return render(
        request,
        "terminal_pagos/terminal_pagos.html",
        {
            "factura_form": factura_form,
            "item_formset": item_formset,
            "productos_json": list(productos),
            "servicios_json": list(servicios),
            "origenes_canales_json": list(origenes_canales),
            "cuentas_json": list(cuentas),
            "today": now().date().isoformat(),
        }
    )


# =========================
# CREAR FACTURA
# =========================
def crear_factura(request):
    if request.method == "POST":
        factura_form = FacturaForm(request.POST)
        factura = Factura()
        item_formset = ItemFacturaFormSet(request.POST, instance=factura)

        if factura_form.is_valid() and item_formset.is_valid():
            factura = factura_form.save()
            item_formset.instance = factura
            item_formset.save()

            return redirect("terminal_pagos:nueva_transaccion")

    else:
        factura_form = FacturaForm()
        item_formset = ItemFacturaFormSet()

    return render(
        request,
        "terminal_pagos/crear_factura.html",
        {
            "factura_form": factura_form,
            "item_formset": item_formset,
        }
    )


# =========================
# CATÁLOGOS DE CONFIGURACIÓN DE PAGOS
# =========================
def catalogos_pago(request):
    origen_id = request.GET.get("origen")
    canal_id = request.GET.get("canal")
    cuenta_id = request.GET.get("cuenta")
    config_id = request.GET.get("config")

    origen_instance = OrigenFondo.objects.filter(id=origen_id).first()
    canal_instance = CanalPago.objects.filter(id=canal_id).first()
    cuenta_instance = Cuenta.objects.filter(id=cuenta_id).first()
    config_instance = OrigenCanal.objects.filter(id=config_id).first()

    origen_form = OrigenFondoForm(
        request.POST or None,
        instance=origen_instance,
        prefix="origen"
    )

    canal_form = CanalPagoForm(
        request.POST or None,
        instance=canal_instance,
        prefix="canal"
    )

    cuenta_form = CuentaForm(
        request.POST or None,
        instance=cuenta_instance,
        prefix="cuenta"
    )

    config_form = OrigenCanalForm(
        request.POST or None,
        instance=config_instance,
        prefix="config"
    )

    if request.method == "POST":
        if "guardar_origen" in request.POST and origen_form.is_valid():
            origen_form.save()
            return redirect("terminal_pagos:catalogos_pago")

        if "guardar_canal" in request.POST and canal_form.is_valid():
            canal_form.save()
            return redirect("terminal_pagos:catalogos_pago")

        if "guardar_cuenta" in request.POST and cuenta_form.is_valid():
            cuenta_form.save()
            return redirect("terminal_pagos:catalogos_pago")

        if "guardar_config" in request.POST and config_form.is_valid():
            config_form.save()
            return redirect("terminal_pagos:catalogos_pago")

    return render(
        request,
        "terminal_pagos/catalogos_pago.html",
        {
            "origenes": OrigenFondo.objects.all(),
            "canales": CanalPago.objects.all(),
            "cuentas": Cuenta.objects.all(),
            "configuraciones": OrigenCanal.objects.select_related(
                "origen", "canal"
            ),
            "origen_form": origen_form,
            "canal_form": canal_form,
            "cuenta_form": cuenta_form,
            "config_form": config_form,
        }
    )
