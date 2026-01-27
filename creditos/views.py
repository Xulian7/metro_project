from django.shortcuts import render, redirect
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from .models import Credito, CreditoItem
from .forms import CreditoForm
from almacen.models import Producto
from taller.models import Servicio
from django.shortcuts import get_object_or_404, render
from .models import Credito


def crear_credito(request):

    # =========================
    # POST → crear crédito
    # =========================
    if request.method == "POST":
        form = CreditoForm(request.POST)

        if form.is_valid():
            with transaction.atomic():

                # ===== CABECERA =====
                credito = form.save(commit=False)
                credito.monto_total = 0
                credito.saldo = 0
                credito.save()

                total = 0

                # ===== LISTAS PARALELAS =====
                tipos = request.POST.getlist("item_tipo[]")
                descripciones = request.POST.getlist("item_descripcion[]")
                cantidades = request.POST.getlist("item_cantidad[]")
                valores = request.POST.getlist("item_valor[]")
                subtotales = request.POST.getlist("item_subtotal[]")

                # ===== ITERACIÓN SEGURA =====
                for tipo, desc, cant, val, sub in zip(
                    tipos, descripciones, cantidades, valores, subtotales
                ):
                    # 🔴 EFECTIVO
                    if tipo == "efectivo":
                        if not val:
                            continue

                        subtotal = float(val)

                        CreditoItem.objects.create(
                            credito=credito,
                            tipo="efectivo",
                            descripcion="Préstamo en efectivo",
                            cantidad=1,
                            valor_unitario=subtotal,
                            subtotal=subtotal
                        )

                        total += subtotal
                        continue

                    # 🔵 ALMACÉN / TALLER
                    if not desc or not sub:
                        continue

                    cantidad = int(cant) if cant else 1
                    valor_unitario = float(val) if val else 0
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

                # ===== TOTALES =====
                credito.monto_total = total
                credito.saldo = total
                credito.save()

            # volver al mismo template (crear + listar)
            return redirect("creditos:crear_credito")

    # =========================
    # GET → formulario + tabla
    # =========================
    else:
        form = CreditoForm()

    creditos = Credito.objects.select_related("contrato").all()

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
            "creditos": creditos,
            "productos": list(productos),
            "servicios": list(servicios),
        }
    )

        



def popover_items_credito(request, credito_id):
    credito = get_object_or_404(Credito, id=credito_id)

    items = credito.items.all() # type: ignore

    return render(
        request,
        "creditos/_popover_items.html",
        {
            "credito": credito,
            "items": items,
        }
    )
