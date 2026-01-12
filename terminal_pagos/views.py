from django.shortcuts import render, redirect
from django.utils.timezone import now

from .models import (
    Factura,
    Cuenta,
    MedioPago,
    CanalPago,
    ConfiguracionPago,
    PagoFactura,
)

from .forms import (
    FacturaForm,
    ItemFacturaFormSet,
    CuentaForm,
    MedioPagoForm,
    CanalPagoForm,
    ConfiguracionPagoForm,
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

    # ⚠️ JSON CLAVE PARA UX GUIADO
    # La verdad sale SOLO de ConfiguracionPago
    configuraciones = ConfiguracionPago.objects.select_related(
        "canal__medio",
        "cuenta_destino"
    ).filter(
        activo=True,
        canal__activo=True,
        canal__medio__activo=True,
        cuenta_destino__activa=True
    ).values(
        # Identidad real de la configuración (esto es lo que se guarda)
        "id",

        # Medio (heredado del canal)
        "canal__medio_id",
        "canal__medio__nombre",

        # Canal
        "canal_id",
        "canal__nombre",
        "canal__requiere_referencia",

        # Cuenta destino (informativa)
        "cuenta_destino__nombre",
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

            # JSONs para frontend
            "productos_json": list(productos),
            "servicios_json": list(servicios),
            "configuraciones_json": list(configuraciones),

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
# CATÁLOGOS DE MEDIOS DE PAGO (ADMIN)
# =========================
def catalogos_pago(request):
    medio_id = request.GET.get("medio")
    canal_id = request.GET.get("canal")
    cuenta_id = request.GET.get("cuenta")
    config_id = request.GET.get("config")

    medio_instance = MedioPago.objects.filter(id=medio_id).first()
    canal_instance = CanalPago.objects.filter(id=canal_id).first()
    cuenta_instance = Cuenta.objects.filter(id=cuenta_id).first()
    config_instance = ConfiguracionPago.objects.filter(id=config_id).first()

    medio_form = MedioPagoForm(
        request.POST or None,
        instance=medio_instance,
        prefix="medio"
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

    config_form = ConfiguracionPagoForm(
        request.POST or None,
        instance=config_instance,
        prefix="config"
    )

    if request.method == "POST":

        if "guardar_medio" in request.POST and medio_form.is_valid():
            medio_form.save()
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
            "medios": MedioPago.objects.all(),
            "canales": CanalPago.objects.select_related("medio"),
            "cuentas": Cuenta.objects.all(),
            "configuraciones": ConfiguracionPago.objects.select_related(
                "canal__medio",
                "cuenta_destino"
            ),
            "medio_form": medio_form,
            "canal_form": canal_form,
            "cuenta_form": cuenta_form,
            "config_form": config_form,
        }
    )
