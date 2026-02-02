from django.db.models import Sum
from terminal_pagos.models import PagoFactura


def totales_por_medio(operador, inicio, fin):
    """
    Devuelve totales agrupados SOLO por medio de pago
    para facturas creadas por el operador activo
    dentro del periodo [inicio, fin]
    """

    qs = (
        PagoFactura.objects
        .filter(
            factura__creado_por=operador,
            factura__estado="confirmada",
            factura__fecha__gte=inicio,
            factura__fecha__lt=fin,
        )
        .values(
            "configuracion__medio_id",
            "configuracion__medio__nombre",
        )
        .annotate(
            total=Sum("valor")
        )
        .order_by("configuracion__medio__nombre")
    )

    # 🔁 Normalizamos claves para el template
    return [
        {
            "medio_id": row["configuracion__medio_id"],
            "medio__nombre": row["configuracion__medio__nombre"],
            "total": row["total"] or 0,
        }
        for row in qs
    ]


from django.utils import timezone
from terminal_pagos.models import PagoFactura
from reportes.models import CierreCaja


def obtener_periodo_operador(operador):
    """
    Devuelve (inicio, fin) del periodo a cerrar para un operador.
    """

    ahora = timezone.now()

    # 1️⃣ Último cierre del operador
    ultimo_cierre = (
        CierreCaja.objects
        .filter(operador=operador)
        .order_by("-fecha_fin")
        .first()
    )

    if ultimo_cierre:
        # 🔁 Continuidad exacta
        inicio = ultimo_cierre.fecha_fin
        return inicio, ahora

    # 2️⃣ Nunca ha cerrado → buscar primer pago válido del operador
    primer_pago = (
        PagoFactura.objects
        .filter(
            factura__creado_por=operador,
            factura__estado="confirmada",
            es_compensacion=False,
        )
        .select_related("factura")
        .order_by("fecha_pago")
        .first()
    )

    if primer_pago:
        # ⏪ Arranca desde el primer movimiento real
        inicio = primer_pago.fecha_pago
        return inicio, ahora

    # 3️⃣ Caso extremo: no hay nada (operador nuevo)
    return ahora, ahora
