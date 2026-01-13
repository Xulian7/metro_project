from django.shortcuts import render, redirect
from django.utils.timezone import now
from almacen.models import Producto
from taller.models import Servicio


from .models import (
    Factura,
    Cuenta,
    MedioPago,
    CanalPago,
    ConfiguracionPago,
)

from .forms import (
    FacturaForm,
    ItemFacturaFormSet,
    CuentaForm,
    MedioPagoForm,
    CanalPagoForm,
    ConfiguracionPagoForm,
)


# =========================
# TERMINAL DE PAGOS
# =========================
def nueva_transaccion(request):

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

    configuraciones = ConfiguracionPago.objects.select_related(
        "medio",
        "cuenta_destino"
    ).filter(
        activo=True,
        medio__activo=True,
        cuenta_destino__activa=True
    ).values(
        "id",

        # Medio
        "medio_id",
        "medio__nombre",

        # Cuenta destino
        "cuenta_destino__nombre",
    )

    canales = CanalPago.objects.filter(
        activo=True,
        medio__activo=True
    ).values(
        "id",
        "medio_id",
        "nombre",
        "requiere_referencia",
        "activo",
    )

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
            "configuraciones_json": list(configuraciones),
            "canales_json": list(canales),
            "today": now().date().isoformat(),
        }
    )
    
    


from django.db import transaction
from decimal import Decimal

from .models import (
    Factura,
    ItemFactura,
    PagoFactura,
    ConfiguracionPago,
    CanalPago,
)


# =========================
# CREAR FACTURA (COMPLETO + DEBUG)
# =========================
def crear_factura(request):
    print("===> ENTRÓ A crear_factura")

    if request.method == "POST":
        print("===> MÉTODO POST")

        factura_form = FacturaForm(request.POST)
        print("Factura form valid:", factura_form.is_valid())
        print("Factura form errors:", factura_form.errors)

        if factura_form.is_valid():
            factura = factura_form.save(commit=False)
            print("Factura creada en memoria (no guardada)")

            item_formset = ItemFacturaFormSet(request.POST, instance=factura)
            print("Item formset valid:", item_formset.is_valid())
            print("Item formset errors:", item_formset.errors)

            if item_formset.is_valid():
                factura.save()
                print(f"Factura GUARDADA con ID: {factura.id}")

                items = item_formset.save(commit=False)

                total_factura = 0

                for item in items:
                    # 🔑 BACKEND MANDA
                    item.factura = factura
                    item.subtotal = item.cantidad * item.valor_unitario
                    total_factura += item.subtotal
                    item.save()

                    print(
                        f"Item guardado | "
                        f"tipo={item.tipo_item} | "
                        f"cantidad={item.cantidad} | "
                        f"unit={item.valor_unitario} | "
                        f"subtotal={item.subtotal}"
                    )

                factura.total = total_factura
                factura.save()

                print(f"TOTAL FACTURA: {factura.total}")

                return redirect("terminal_pagos:nueva_transaccion")

            else:
                print("❌ Item formset NO válido")

        else:
            print("❌ Factura form NO válido")

    else:
        print("===> MÉTODO GET")
        factura_form = FacturaForm()
        item_formset = ItemFacturaFormSet()

    return render(
        request,
        "terminal_pagos/terminal_pagos.html",
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

    medio_form = MedioPagoForm(
        request.POST or None,
        instance=MedioPago.objects.filter(id=medio_id).first(),
        prefix="medio"
    )

    canal_form = CanalPagoForm(
        request.POST or None,
        instance=CanalPago.objects.filter(id=canal_id).first(),
        prefix="canal"
    )

    cuenta_form = CuentaForm(
        request.POST or None,
        instance=Cuenta.objects.filter(id=cuenta_id).first(),
        prefix="cuenta"
    )

    config_form = ConfiguracionPagoForm(
        request.POST or None,
        instance=ConfiguracionPago.objects.filter(id=config_id).first(),
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
                "medio",
                "cuenta_destino"
            ),
            "medio_form": medio_form,
            "canal_form": canal_form,
            "cuenta_form": cuenta_form,
            "config_form": config_form,
        }
    )
