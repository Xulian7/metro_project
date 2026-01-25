from django.shortcuts import render, redirect
from django.db import transaction
from .models import Credito, CreditoItem
from .forms import CreditoForm


def crear_credito(request):
    """
    Crear un crédito con sus items.
    """

    if request.method == "POST":
        form = CreditoForm(request.POST)

        if form.is_valid():
            with transaction.atomic():

                credito = form.save(commit=False)
                credito.monto_total = 0
                credito.saldo = 0
                credito.save()

                total = 0

                # Items vienen como listas paralelas
                descripciones = request.POST.getlist("item_descripcion[]")
                cantidades = request.POST.getlist("item_cantidad[]")
                valores = request.POST.getlist("item_valor[]")
                subtotales = request.POST.getlist("item_subtotal[]")

                for i in range(len(descripciones)):
                    subtotal = float(subtotales[i])

                    CreditoItem.objects.create(
                        credito=credito,
                        descripcion=descripciones[i],
                        cantidad=cantidades[i] or None,
                        valor_unitario=valores[i] or None,
                        subtotal=subtotal
                    )

                    total += subtotal

                credito.monto_total = total
                credito.saldo = total
                credito.save()

            return redirect("creditos:listar_creditos")

    else:
        form = CreditoForm()

    return render(
        request,
        "creditos/crear_credito.html",
        {
            "form": form
        }
    )
