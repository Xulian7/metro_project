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
