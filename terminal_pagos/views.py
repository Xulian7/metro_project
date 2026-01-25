from django.shortcuts import render, redirect
from django.utils.timezone import now
from almacen.models import Producto
from taller.models import Servicio
from django.db import transaction
from .models import PagoFactura, ConfiguracionPago, CanalPago
from .forms import FacturaForm, ItemFacturaFormSet
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
from decimal import Decimal
from datetime import date, timedelta
from arrendamientos.models import Contrato
from terminal_pagos.models import Factura, ItemFactura
from django.http import JsonResponse


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
    
    # -------------------------------------------------
    # FACTURA RECIÉN CREADA (si viene por GET)
    # -------------------------------------------------
    factura_id = request.GET.get("factura")
    factura = None

    if factura_id:
        try:
            factura = (
                Factura.objects
                .prefetch_related(
                    "items",
                    "pagos__configuracion__medio",
                    "pagos__canal",
                )
                .get(id=factura_id)
            )
        except Factura.DoesNotExist:
            factura = None

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
            "factura": factura,
        }
    )
    
# =========================
# CREAR FACTURA + ÍTEMS + PAGOS
# =========================
@transaction.atomic
def crear_factura(request):

    print("🚀 [crear_factura] INICIO")

    # -------------------------------------------------
    # 1. VALIDAR MÉTODO
    # -------------------------------------------------
    if request.method != "POST":
        print("⚠️ Método no POST, redirigiendo")
        return redirect("terminal_pagos:nueva_transaccion")

    # -------------------------------------------------
    # 2. FACTURA
    # -------------------------------------------------
    factura_form = FacturaForm(request.POST)

    if not factura_form.is_valid():
        print("❌ Factura inválida")
        print("   Errores:", factura_form.errors)
        return redirect("terminal_pagos:nueva_transaccion")

    factura = factura_form.save()
    print(f"✅ Factura creada | ID={factura.id}")

    # -------------------------------------------------
    # 3. ÍTEMS
    # -------------------------------------------------
    item_formset = ItemFacturaFormSet(request.POST, instance=factura)

    if not item_formset.is_valid():
        print("❌ Ítems inválidos")
        print("   Errores:", item_formset.errors)
        return redirect("terminal_pagos:nueva_transaccion")

    items = item_formset.save(commit=False)
    total_factura = Decimal("0.00")


    print(f"🧾 Procesando {len(items)} ítems")

    for i, item in enumerate(items, start=1):
        print(f"➡️ Ítem #{i} | tipo={item.tipo_item} | raw='{item.descripcion}'")

        item.factura = factura
        raw = item.descripcion or ""

        # ---- TARIFA ----
        if item.tipo_item == "tarifa":
            item.descripcion = "Pago de tarifa"
            item.producto_almacen = None
            item.servicio_taller = None
            print("   ↳ Tarifa aplicada")

        # ---- ALMACÉN ----
        elif item.tipo_item == "almacen" and ":" in raw:
            _, producto_id = raw.split(":", 1)
            producto = Producto.objects.get(id=int(producto_id))
            item.producto_almacen = producto
            item.servicio_taller = None
            item.descripcion = producto.nombre
            print(f"   ↳ Producto almacén ID={producto.id}") # type: ignore

        # ---- TALLER ----
        elif item.tipo_item == "taller" and ":" in raw:
            _, servicio_id = raw.split(":", 1)
            servicio = Servicio.objects.get(id=int(servicio_id))
            item.servicio_taller = servicio
            item.producto_almacen = None
            item.descripcion = servicio.nombre_servicio
            print(f"   ↳ Servicio taller ID={servicio.id}") # type: ignore

        # ---- SUBTOTAL ----
        item.subtotal =  item.valor_unitario
        item.save()

        total_factura += item.subtotal

        print(
            f"   💾 Guardado | cantidad={item.cantidad} | "
            f"unitario={item.valor_unitario} | subtotal={item.subtotal}"
        )

    print(f"🧮 Total factura calculado = {total_factura}")

    # -------------------------------------------------
    # 4. PAGOS
    # -------------------------------------------------
    configuraciones_ids = request.POST.getlist("configuracion_pago_id[]")
    canales_ids = request.POST.getlist("canal_pago[]")
    valores = request.POST.getlist("valor_pago[]")
    referencias = request.POST.getlist("referencia_pago[]")

    total_pagado = Decimal("0.00")

    print(f"💳 Procesando pagos | filas={len(valores)}")
    print(request.POST.getlist("configuracion_pago_id[]"))
    print(request.POST.getlist("canal_pago[]"))
    print(request.POST.getlist("valor_pago[]"))
    print(request.POST.getlist("referencia_pago[]"))


    for i in range(len(valores)):
        valor = valores[i]
        config_id = configuraciones_ids[i] if i < len(configuraciones_ids) else None
        canal_id = canales_ids[i] if i < len(canales_ids) else None
        referencia = referencias[i] if i < len(referencias) else ""

        print(
            f"➡️ Pago #{i+1} | "
            f"valor='{valor}' | "
            f"config={config_id} | "
            f"canal={canal_id}"
        )

        if not valor or not config_id or not canal_id:
            print(
                f"➡️ Pago #{i+1} | "
                f"valor='{valor}' | "
                f"config={config_id} | "
                f"canal={canal_id}"
                f"⚠️ Fila incompleta, se ignora"
            )
            
            continue

        try:
            configuracion = ConfiguracionPago.objects.get(id=int(config_id))
            canal = CanalPago.objects.get(id=int(canal_id))
            valor = Decimal(valor)
        except Exception as e:
            print("   ❌ Pago inválido:", e)
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
            f"   💾 Pago guardado | "
            f"{configuracion.medio} - {canal.nombre} | {valor}"
        )

    print(f"💰 Total pagado = {total_pagado}")

    # -------------------------------------------------
    # 5. TOTALES Y ESTADO
    # -------------------------------------------------
    factura.total = total_factura
    factura.total_pagado = total_pagado

    # ---- ESTADO DE PAGO ----
    if total_pagado == Decimal("0.00"):
        factura.estado_pago = "pendiente"
    elif total_pagado < total_factura:
        factura.estado_pago = "parcial"
    else:
        factura.estado_pago = "pagada"
        
    # ---- ESTADO ADMINISTRATIVO ----
    if factura.estado_pago == "pagada":
        factura.estado = "confirmada"
    else:
        factura.estado = "borrador"

    factura.save()
        
    print(
        f"🎉 FACTURA FINALIZADA | "
        f"Total={factura.total} | "
        f"Pagado={factura.total_pagado} | "
        f"Estado={factura.estado_pago}"
    )

    print("✅ [crear_factura] FIN OK")
    
    return redirect(f"{reverse('terminal_pagos:nueva_transaccion')}?factura={factura.id}")
    


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

# =========================
# LISTADO DE PAGOS REALIZADOS
# =========================
def medios_pago(request):
    """
    Listado de pagos con factura y contrato
    Filtro opcional por rango de fechas
    """

    pagos = (
        PagoFactura.objects
        .select_related(
            "factura",
            "factura__contrato",
            "factura__contrato__vehiculo",
            "factura__contrato__cliente",
            "configuracion",
            "configuracion__medio",
            "configuracion__cuenta_destino",
            "canal",
        )
        .order_by("-fecha_pago")
    )

    # -------------------------
    # FILTROS DE FECHA (GET)
    # -------------------------
    desde = request.GET.get("desde")
    hasta = request.GET.get("hasta")

    if desde:
        pagos = pagos.filter(fecha_pago__gte=desde)

    if hasta:
        pagos = pagos.filter(fecha_pago__lte=hasta)

    context = {
        "pagos": pagos,
        "desde": desde,
        "hasta": hasta,
    }

    return render(
        request,
        "terminal_pagos/medios_pago.html",
        context
    )


@require_POST
def validar_pago(request, pago_id):
    pago = get_object_or_404(PagoFactura, id=pago_id)
    pago.validado = True
    pago.save(update_fields=["validado"])
    print("✅ Pago validado")
    return HttpResponse(status=204)



from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum
from django.shortcuts import render
from arrendamientos.models import Contrato
from terminal_pagos.models import ItemFactura


def resumen_contratos(request):
    hoy = date.today()
    filas = []

    contratos = (
        Contrato.objects
        .select_related("cliente", "vehiculo")
        .filter(estado="Activo")
    )

    for contrato in contratos:
        if not contrato.fecha_inicio or not contrato.tarifa:
            continue

        # -------------------------
        # ANTIGÜEDAD
        # -------------------------
        dias_transcurridos = (hoy - contrato.fecha_inicio).days
        if dias_transcurridos < 0:
            dias_transcurridos = 0

        # -------------------------
        # CUOTAS VENCIDAS
        # -------------------------
        dias_por_cuota = {
            "Diario": 1,
            "Semanal": 7,
            "Quincenal": 15,
            "Mensual": 30,
        }.get(contrato.frecuencia_pago, 30)

        cuotas_vencidas = Decimal(
            dias_transcurridos / dias_por_cuota
        ).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

        # -------------------------
        # PAGOS EN TARIFA
        # -------------------------
        total_pagado = (
            ItemFactura.objects
            .filter(
                tipo_item="tarifa",
                factura__contrato=contrato
            )
            .aggregate(total=Sum("subtotal"))["total"]
            or Decimal("0")
        )

        cuotas_pagadas = (
            total_pagado / contrato.tarifa
        ).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

        # -------------------------
        # SALDO (cuotas + dinero)
        # -------------------------
        saldo_cuotas = (
            cuotas_vencidas - cuotas_pagadas
        ).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

        saldo_dinero = (
            saldo_cuotas * contrato.tarifa
        ).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

        filas.append({
            "contrato": contrato,
            "fecha_inicio": contrato.fecha_inicio,
            "dias_transcurridos": dias_transcurridos,
            "tarifa": contrato.tarifa,
            "frecuencia": contrato.get_frecuencia_pago_display(), # type: ignore
            "cuotas_vencidas": cuotas_vencidas,
            "cuotas_pagadas": cuotas_pagadas,
            "total_pagado": total_pagado,
            "saldo_cuotas": saldo_cuotas,
            "saldo_dinero": saldo_dinero,  # 👈 NUEVO
        })

    return render(
        request,
        "terminal_pagos/resumen_contratos.html",
        {
            "filas": filas,
            "hoy": hoy,
        }
    )


def extracto_contrato(request, contrato_id):
    contrato = get_object_or_404(Contrato, id=contrato_id)

    tarifa = contrato.tarifa
    inicio = contrato.fecha_inicio
    hoy = date.today()

    # -------------------------
    # 1. Generar fechas pactadas
    # -------------------------
    fechas = []
    actual = inicio

    delta = {
        "Diario": 1,
        "Semanal": 7,
        "Quincenal": 15,
        "Mensual": 30,
    }.get(contrato.frecuencia_pago, 30)

    while actual <= hoy:
        fechas.append({
            "fecha_pactada": actual,
            "valor_pactado": tarifa,
            "valor_aplicado": Decimal("0.00"),
            "fecha_pago": None,
            "factura_id": None,
        })
        actual += timedelta(days=delta)

    # -------------------------
    # 2. Obtener ladrillos (items tarifa)
    # -------------------------
    items = (
        ItemFactura.objects
        .filter(
            factura__contrato=contrato,
            tipo_item="tarifa"
        )
        .select_related("factura")
        .order_by("factura__fecha")
    )

    idx_fecha = 0

    # -------------------------
    # 3. TETRIS FIFO ESTRICTO
    # -------------------------
    for item in items:
        saldo = item.subtotal

        while saldo > 0 and idx_fecha < len(fechas):
            fila = fechas[idx_fecha]
            restante = fila["valor_pactado"] - fila["valor_aplicado"]

            if restante <= 0:
                idx_fecha += 1
                continue

            aplicado = min(restante, saldo)

            fila["valor_aplicado"] += aplicado
            fila["fecha_pago"] = item.factura.fecha.date()
            fila["factura_id"] = item.factura.id # type: ignore

            saldo -= aplicado

            if fila["valor_aplicado"] >= fila["valor_pactado"]:
                idx_fecha += 1
            else:
                break  # ← última fila parcial

    # -------------------------
    # 4. Respuesta JSON
    # -------------------------
    return JsonResponse({
        "filas": [
            {
                "fecha_pactada": f["fecha_pactada"].isoformat(),
                "valor_pactado": float(f["valor_pactado"]),
                "valor_aplicado": float(f["valor_aplicado"]),
                "fecha_pago": f["fecha_pago"].isoformat() if f["fecha_pago"] else None,
                "factura_id": f["factura_id"],
            }
            for f in fechas
        ]
    })
    
    
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from decimal import Decimal

def detalle_factura_pagos(request, factura_id):

    factura = get_object_or_404(
        Factura.objects.prefetch_related(
            "pagos__configuracion__medio",
            "pagos__canal",
        ),
        id=factura_id
    )

    pagos = factura.pagos.all().order_by("id") # type: ignore

    return JsonResponse({
        "factura": {
            "id": factura.id, # type: ignore
            "fecha": factura.fecha.strftime("%d/%m/%Y %H:%M"),
            "total": str(factura.total),
            "total_pagado": str(factura.total_pagado),
            "estado_pago": factura.get_estado_pago_display(), # type: ignore
        },
        "pagos": [
            {
                "medio": p.configuracion.medio.nombre,
                "canal": p.canal.nombre,
                "valor": str(p.valor),      # 👈 NO float
                "referencia": p.referencia or "",
            }
            for p in pagos
        ]
    })

