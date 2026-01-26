from django.shortcuts import render, redirect
from django.db import transaction
from .models import Credito, CreditoItem
from .forms import CreditoForm

from almacen.models import Producto
from taller.models import Servicio


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

                # 🔑 listas paralelas
                tipos = request.POST.getlist("item_tipo[]")
                descripciones = request.POST.getlist("item_descripcion[]")
                observaciones = request.POST.getlist("item_observacion[]")
                cantidades = request.POST.getlist("item_cantidad[]")
                valores = request.POST.getlist("item_valor[]")
                subtotales = request.POST.getlist("item_subtotal[]")

                for i in range(len(descripciones)):
                    if not descripciones[i] or not subtotales[i]:
                        continue  # seguridad extra

                    subtotal = float(subtotales[i])

                    CreditoItem.objects.create(
                        credito=credito,
                        tipo=tipos[i],
                        descripcion=descripciones[i],
                        observacion=observaciones[i],
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

    # 📦 Datos para selects
    productos = Producto.objects.all().values(
        "nombre", "precio_venta"
    )

    servicios = Servicio.objects.all().values(
        "nombre_servicio", "valor"
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
