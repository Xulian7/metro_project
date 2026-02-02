from django.utils import timezone
from django.db.models import Sum
from terminal_pagos.models import PagoFactura
from reportes.models import CierreCaja

def obtener_periodo_operador(operador):
    ultimo = (
        CierreCaja.objects
        .filter(operador=operador, autorizado=True)
        .order_by("-fecha_fin")
        .first()
    )

    inicio = ultimo.fecha_fin if ultimo else operador.date_joined
    fin = timezone.now()

    return inicio, fin


def totales_por_medio(operador, inicio, fin):
    return (
        PagoFactura.objects
        .filter(
            creado_por=operador,
            fecha_pago__range=(inicio, fin),
            validado=True,
        )
        .values(
            "configuracion__medio__nombre",
            "configuracion__cuenta_destino__nombre",
        )
        .annotate(total=Sum("valor"))
    )
