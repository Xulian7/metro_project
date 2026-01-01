from django.shortcuts import render, redirect
from .models import Factura
from .forms import FacturaForm, ItemFacturaFormSet


def crear_factura(request):
    if request.method == "POST":
        factura_form = FacturaForm(request.POST)
        factura = Factura()

        item_formset = ItemFacturaFormSet(request.POST, instance=factura)

        if factura_form.is_valid() and item_formset.is_valid():
            factura = factura_form.save()
            item_formset.instance = factura
            item_formset.save()

            return redirect("terminal_pagos:crear_factura")

    else:
        factura_form = FacturaForm()
        item_formset = ItemFacturaFormSet()

    context = {
        "factura_form": factura_form,
        "item_formset": item_formset,
    }

    return render(request, "terminal_pagos/crear_factura.html", context)
