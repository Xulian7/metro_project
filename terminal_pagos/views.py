from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction

from arrendamientos.models import Contrato
from terminal_pagos.models import (
    MedioPago,
    ItemFactura,
)

def terminal_pagos(request):
    contratos = Contrato.objects.select_related(
        "vehiculo",
        "cliente"
    ).all()

    medios_pago = MedioPago.objects.filter(activo=True)

    # Tipos de item directamente desde el modelo
    tipos_item = ItemFactura.TIPOS

    if request.method == "POST":
        # MVP: solo capturamos, la lógica dura viene después
        messages.success(
            request,
            "Transacción capturada correctamente (modo MVP 😎)"
        )
        return redirect("terminal_pagos")

    context = {
        "contratos": contratos,
        "medios_pago": medios_pago,
        "tipos_item": tipos_item,
    }

    return render(
        request,
        "terminal_pagos/terminal.html",
        context
    )
