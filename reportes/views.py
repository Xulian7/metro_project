from decimal import Decimal
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from reportes.models import CierreCaja, CierreCajaDetalle
from reportes.services.cierres import obtener_periodo_operador, totales_por_medio
from terminal_pagos.models import MedioPago


@login_required
@permission_required("reportes.add_cierrecaja", raise_exception=True)
def nuevo_cierre(request):

    operador = request.user

    # =========================
    # 1️⃣ PERIODO DEL CIERRE
    # =========================
    inicio, fin = obtener_periodo_operador(operador)

    # =========================
    # 2️⃣ TOTALES POR MEDIO
    # =========================
    totales = totales_por_medio(operador, inicio, fin)
    
    # últimos 10 cierres del operador
    ultimos_cierres = (
        CierreCaja.objects
        .filter(operador=operador)
        .order_by("-fecha_fin")[:10]
    )

    if request.method == "POST":

        total_sistema = Decimal("0")
        total_arqueo = Decimal("0")

        # =========================
        # 3️⃣ CREAR CIERRE
        # =========================
        cierre = CierreCaja.objects.create(
            operador=operador,
            fecha_inicio=inicio,
            fecha_fin=timezone.now(),
            total_sistema=Decimal("0"),
            total_arqueo=Decimal("0"),
            diferencia=Decimal("0"),
            observacion=request.POST.get("observacion", "").strip(),
        )

        # =========================
        # 4️⃣ DETALLE POR MEDIO
        # =========================
        for i, fila in enumerate(totales, start=1):

            sistema = Decimal(fila["total"] or 0)

            arqueo = Decimal(
                request.POST.get(f"arqueo_{i}", "0") or "0"
            )

            medio = get_object_or_404(
                MedioPago,
                id=fila["medio_id"]
            )

            diferencia = arqueo - sistema

            CierreCajaDetalle.objects.create(
                cierre=cierre,
                medio=medio,
                total_sistema=sistema,
                total_arqueo=arqueo,
                diferencia=diferencia,
            )

            total_sistema += sistema
            total_arqueo += arqueo

        # =========================
        # 5️⃣ TOTALES GENERALES
        # =========================
        cierre.total_sistema = total_sistema
        cierre.total_arqueo = total_arqueo
        cierre.diferencia = total_arqueo - total_sistema
        cierre.save()

        return redirect(
            "reportes:detalle_cierre",
            cierre_id=cierre.id # type: ignore
        )

    # =========================
    # 6️⃣ FORMULARIO
    # =========================
    return render(
        request,
        "reportes/nuevo_cierre.html",
        {
            "inicio": inicio,
            "fin": fin,
            "totales": totales,
            "ultimos_cierres": ultimos_cierres,
        }
    )

from django.shortcuts import render, get_object_or_404
from reportes.models import CierreCaja

def detalle_cierre(request, cierre_id):
    cierre = get_object_or_404(CierreCaja, id=cierre_id)

    return render(
        request,
        "reportes/detalle_cierre.html",
        {"cierre": cierre}
    )


from datetime import date
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Sum, Count
from django.shortcuts import render

from terminal_pagos.models import ItemFactura, PagoFactura


@login_required
@permission_required("reportes.view_reportes", raise_exception=True)
def dashboard_reportes(request):

    # =========================
    # 1️⃣ RANGO DE FECHAS
    # =========================
    inicio = request.GET.get("inicio") or date.today().replace(day=1)
    fin = request.GET.get("fin") or date.today()

    # =========================
    # 2️⃣ ITEMS POR TIPO
    # =========================
    items = (
        ItemFactura.objects
        .filter(
            factura__estado="confirmada",
            factura__fecha__date__range=[inicio, fin]
        )
        .values("tipo_item")
        .annotate(
            cantidad=Count("id"),
            total=Sum("subtotal")
        )
        .order_by("tipo_item")
    )

    # =========================
    # 3️⃣ PAGOS POR MEDIO
    # =========================
    pagos = (
        PagoFactura.objects
        .filter(
            factura__estado="confirmada",
            fecha_pago__range=[inicio, fin],
            es_compensacion=False
        )
        .values(
            "configuracion__medio__nombre"
        )
        .annotate(
            total=Sum("valor")
        )
        .order_by("configuracion__medio__nombre")
    )

    # =========================
    # 4️⃣ TOTALES POR CUENTA
    # =========================
    cuentas = (
        PagoFactura.objects
        .filter(
            factura__estado="confirmada",
            fecha_pago__range=[inicio, fin],
            es_compensacion=False
        )
        .values(
            "configuracion__cuenta_destino__nombre"
        )
        .annotate(
            total=Sum("valor")
        )
        .order_by("configuracion__cuenta_destino__nombre")
    )

    # =========================
    # 5️⃣ RENDER
    # =========================
    return render(
        request,
        "reportes/dashboard_reportes.html",
        {
            "inicio": inicio,
            "fin": fin,
            "items": items,
            "pagos": pagos,
            "cuentas": cuentas,
        }
    )
