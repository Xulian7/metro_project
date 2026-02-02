from decimal import Decimal

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from reportes.models import CierreCaja, CierreCajaDetalle
from reportes.services.cierres import (
    obtener_periodo_operador,
    totales_por_medio,
)

from terminal_pagos.models import ConfiguracionPago


@login_required
@permission_required("reportes.add_cierrecaja", raise_exception=True)
def nuevo_cierre(request):

    operador = request.user

    # =========================
    # 1️⃣ PERIODO DEL CIERRE
    # =========================
    inicio, fin = obtener_periodo_operador(operador)

    # =========================
    # 2️⃣ TOTALES DEL SISTEMA
    # =========================
    # Cada fila:
    # {
    #   "configuracion_id": int,
    #   "medio": str,
    #   "cuenta": str,
    #   "total": Decimal
    # }
    totales = totales_por_medio(operador, inicio, fin)

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
        # 4️⃣ DETALLE POR CONFIGURACIÓN
        # =========================
        for i, fila in enumerate(totales, start=1):

            sistema = Decimal(fila["total"])

            arqueo = Decimal(
                request.POST.get(f"arqueo_{i}", "0") or "0"
            )

            configuracion = get_object_or_404(
                ConfiguracionPago,
                id=fila["configuracion_id"]
            )

            diferencia = arqueo - sistema

            CierreCajaDetalle.objects.create(
                cierre=cierre,
                configuracion=configuracion,
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

        # =========================
        # 6️⃣ REDIRECCIÓN
        # =========================
        return redirect(
            "reportes:detalle_cierre",
            cierre_id=cierre.id # type: ignore
        )

    # =========================
    # 7️⃣ GET → FORMULARIO
    # =========================
    return render(
        request,
        "reportes/nuevo_cierre.html",
        {
            "inicio": inicio,
            "fin": fin,
            "totales": totales,
        }
    )
