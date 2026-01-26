from django.shortcuts import render, redirect
from django.db import transaction
from .models import Credito, CreditoItem
from .forms import CreditoForm

from almacen.models import Producto
from taller.models import Servicio
from django.db.models import F


def crear_credito(request):
    

    if request.method == "POST":
        form = CreditoForm(request.POST)

        if form.is_valid():
            with transaction.atomic():

                # ====== CABECERA ======
                credito = form.save(commit=False)
                credito.monto_total = 0
                credito.saldo = 0
                credito.save()

                total = 0

                # ====== LISTAS PARALELAS ======
                tipos = request.POST.getlist("item_tipo[]")
                descripciones = request.POST.getlist("item_descripcion[]")
                cantidades = request.POST.getlist("item_cantidad[]")
                valores = request.POST.getlist("item_valor[]")
                subtotales = request.POST.getlist("item_subtotal[]")

                # ====== ITERACIÓN SEGURA ======
                for tipo, desc, cant, val, sub in zip(
                    tipos, descripciones, cantidades, valores, subtotales
                ):
                    if not desc or not sub:
                        continue

                    cantidad = int(cant) if cant else None
                    valor_unitario = float(val) if val else None
                    subtotal = float(sub)

                    CreditoItem.objects.create(
                        credito=credito,
                        tipo=tipo,
                        descripcion=desc,
                        cantidad=cantidad,
                        valor_unitario=valor_unitario,
                        subtotal=subtotal
                    )

                    total += subtotal

                # ====== TOTALES ======
                credito.monto_total = total
                credito.saldo = total
                credito.save()

            return redirect("creditos:listar_creditos")

    else:
        form = CreditoForm()

    # ====== DATA PARA EL FRONT ======
    productos = Producto.objects.values(
        "id",
        label=F("nombre"),
        precio=F("precio_venta")
    )

    servicios = Servicio.objects.values(
        "id",
        label=F("nombre_servicio"),
        precio=F("valor")
    )

    return render(
        request,
        "creditos/crear_credito.html",
        {
            "form": form,
            "productos": list(productos),
            "servicios": list(servicios),
        }
    )
