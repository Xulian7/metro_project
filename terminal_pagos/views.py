from django.shortcuts import render, redirect
from django.utils.timezone import now
from almacen.models import Producto
from taller.models import Servicio
from django.db import transaction
from .models import PagoFactura, ConfiguracionPago, CanalPago


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
    
    
# =========================
# CREAR FACTURA + ÍTEMS (PULIDO)
# =========================
@transaction.atomic
def crear_factura(request):
    if request.method != "POST":
        return redirect("terminal_pagos:nueva_transaccion")

    factura_form = FacturaForm(request.POST)

    if not factura_form.is_valid():
        print("❌ Factura inválida:", factura_form.errors)
        return redirect("terminal_pagos:nueva_transaccion")

    factura = factura_form.save()
    print(f"✅ Factura creada ID={factura.id}")

    item_formset = ItemFacturaFormSet(request.POST, instance=factura)

    if not item_formset.is_valid():
        print("❌ Ítems inválidos:", item_formset.errors)
        return redirect("terminal_pagos:nueva_transaccion")

    items = item_formset.save(commit=False)

    total_factura = 0

    for item in items:
        item.factura = factura
        raw = item.descripcion or ""

        if item.tipo_item == "tarifa":
            item.descripcion = "Pago de tarifa"
            item.producto_almacen = None
            item.servicio_taller = None

        elif item.tipo_item == "almacen":
            _, producto_id = raw.split(":", 1)
            producto = Producto.objects.get(id=int(producto_id))
            item.producto_almacen = producto
            item.servicio_taller = None
            item.descripcion = producto.nombre

        elif item.tipo_item == "taller":
            _, servicio_id = raw.split(":", 1)
            servicio = Servicio.objects.get(id=int(servicio_id))
            item.servicio_taller = servicio
            item.producto_almacen = None
            item.descripcion = servicio.nombre_servicio

        item.subtotal = item.cantidad * item.valor_unitario
        item.save()

        total_factura += item.subtotal

        print(
            f"🧾 Ítem guardado | tipo={item.tipo_item} | "
            f"subtotal={item.subtotal}"
        )


    # =========================
    # PAGOS
    # =========================
    configuraciones_ids = request.POST.getlist("configuracion_pago_id[]")
    canales_ids = request.POST.getlist("canal_pago[]")
    valores = request.POST.getlist("valor_pago[]")
    referencias = request.POST.getlist("referencia_pago[]")

    total_pagado = 0

    for config_id, canal_id, valor, referencia in zip(
        configuraciones_ids,
        canales_ids,
        valores,
        referencias,
    ):
        if not valor or not config_id or not canal_id:
            continue

        try:
            configuracion = ConfiguracionPago.objects.get(id=int(config_id))
            canal = CanalPago.objects.get(id=int(canal_id))
            valor = float(valor)
        except Exception as e:
            print("⚠️ Pago inválido:", e)
            continue

        PagoFactura.objects.create(
            factura=factura,
            configuracion=configuracion,
            canal=canal,
            valor=valor,
            referencia=referencia or "",
        )

        total_pagado += valor

        print(
            f"💳 Pago guardado | "
            f"{configuracion.medio} - {canal.nombre} | {valor}"
        )

    # =========================
    # TOTALES Y ESTADO
    # =========================
    factura.total = total_factura
    factura.total_pagado = total_pagado

    if total_pagado == 0:
        factura.estado_pago = "pendiente"
    elif total_pagado < total_factura:
        factura.estado_pago = "parcial"
    else:
        factura.estado_pago = "pagada"

    factura.save()

    print(
        f"🎉 FACTURA COMPLETA | "
        f"Total={factura.total} | "
        f"Pagado={factura.total_pagado} | "
        f"Estado={factura.estado_pago}"
    )

    return redirect("terminal_pagos:nueva_transaccion")



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
