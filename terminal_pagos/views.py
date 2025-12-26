from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction

from arrendamientos.models import Contrato
from terminal_pagos.models import (
    MedioPago,
    TipoItemFactura,
)

def terminal_pagos(request):
    contratos = Contrato.objects.select_related(
        "vehiculo",
        "cliente"
    ).all()

    medios_pago = MedioPago.objects.filter(activo=True)
    tipos_item = TipoItemFactura.objects.all()

    if request.method == "POST":
        # ⚠️ De momento solo capturamos, no persistimos
        # La lógica dura viene después (items + pagos + validaciones)
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
