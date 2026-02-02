from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from .services.cierres import obtener_periodo_operador, totales_por_medio
from decimal import Decimal
from django.shortcuts import redirect
from django.utils import timezone
from reportes.models import CierreCaja, CierreCajaDetalle

@login_required
@permission_required("reportes.add_cierrecaja", raise_exception=True)
def nuevo_cierre(request):

    operador = request.user
    inicio, fin = obtener_periodo_operador(operador)
    totales = totales_por_medio(operador, inicio, fin)

    if request.method == "POST":

        total_sistema = Decimal("0")
        total_arqueo = Decimal("0")

        cierre = CierreCaja.objects.create(
            operador=operador,
            fecha_inicio=inicio,
            fecha_fin=timezone.now(),
            total_sistema=0,
            total_arqueo=0,
            diferencia=0,
            observacion=request.POST.get("observacion", ""),
        )

        for i, _ in enumerate(totales, start=1):
            sistema = Decimal(request.POST.get(f"sistema_{i}", "0"))
            arqueo = Decimal(request.POST.get(f"arqueo_{i}", "0"))

            medio = request.POST.get(f"medio_{i}")
            cuenta = request.POST.get(f"cuenta_{i}")

            diff = arqueo - sistema

            CierreCajaDetalle.objects.create(
                cierre=cierre,
                medio=medio,
                cuenta=cuenta,
                total_sistema=sistema,
                total_arqueo=arqueo,
                diferencia=diff,
            )

            total_sistema += sistema
            total_arqueo += arqueo

        cierre.total_sistema = total_sistema
        cierre.total_arqueo = total_arqueo
        cierre.diferencia = total_arqueo - total_sistema
        cierre.save()

        return redirect("reportes:detalle_cierre", cierre.id) # type: ignore

    return render(request, "reportes/nuevo_cierre.html", {
        "inicio": inicio,
        "fin": fin,
        "totales": totales,
    })
