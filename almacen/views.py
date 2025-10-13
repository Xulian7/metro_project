from django.shortcuts import render, redirect
from django.db.models import Sum, Q
from django.http import HttpResponse
from .models import Producto, Proveedor, Movimiento
from .forms import ProductoForm, ProveedorForm, MovimientoForm
import datetime
import csv


def almacen_dashboard(request):
    """
    Vista principal del módulo de almacén.
    Permite gestionar productos, proveedores y movimientos.
    """
    productos = Producto.objects.all()
    proveedores = Proveedor.objects.all()
    movimientos = Movimiento.objects.order_by('-fecha')

    # ---------------------------
    # FILTROS
    # ---------------------------
    producto_id = request.GET.get('producto')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    tipo_mov = request.GET.get('tipo_mov')  # ingreso/salida

    filtro = Q()
    if producto_id:
        filtro &= Q(producto_id=producto_id)
    if fecha_inicio and fecha_fin:
        filtro &= Q(fecha__range=[fecha_inicio, fecha_fin])
    if tipo_mov in ['ingreso', 'salida']:
        filtro &= Q(tipo__startswith=tipo_mov)

    movimientos = movimientos.filter(filtro)

    # ---------------------------
    # FORMULARIOS
    # ---------------------------
    producto_form = ProductoForm()
    proveedor_form = ProveedorForm()
    movimiento_form = MovimientoForm()

    if request.method == "POST":
        # Crear producto
        if 'producto_submit' in request.POST:
            producto_form = ProductoForm(request.POST)
            if producto_form.is_valid():
                producto_form.save()
                return redirect('almacen_dashboard')

        # Crear proveedor
        elif 'proveedor_submit' in request.POST:
            proveedor_form = ProveedorForm(request.POST)
            if proveedor_form.is_valid():
                proveedor_form.save()
                return redirect('almacen_dashboard')

        # Crear movimiento
        elif 'movimiento_submit' in request.POST:
            movimiento_form = MovimientoForm(request.POST)
            if movimiento_form.is_valid():
                movimiento_form.save()
                return redirect('almacen_dashboard')

        # Exportar CSV
        elif 'export_csv' in request.POST:
            return export_movimientos_csv(movimientos)

    # ---------------------------
    # AGRUPAR MOVIMIENTOS POR PRODUCTO
    # ---------------------------
    movimientos_por_producto = {}
    for producto in productos:
        movimientos_producto = movimientos.filter(producto=producto)
        ingresos = movimientos_producto.filter(tipo__startswith='ingreso')
        salidas = movimientos_producto.filter(tipo__startswith='salida')

        stock_ingresos = ingresos.aggregate(total=Sum('cantidad'))['total'] or 0
        stock_salidas = salidas.aggregate(total=Sum('cantidad'))['total'] or 0
        stock_actual = stock_ingresos - stock_salidas

        valor_ingresos = sum([m.valor_total() for m in ingresos])
        valor_salidas = sum([m.valor_total() for m in salidas])
        valor_stock = valor_ingresos - valor_salidas

        movimientos_por_producto[producto] = {
            "ingresos": ingresos,
            "salidas": salidas,
            "stock_actual": stock_actual,
            "valor_stock": valor_stock
        }

    # ---------------------------
    # CONTEXTO PARA EL TEMPLATE
    # ---------------------------
    context = {
        "productos": productos,
        "proveedores": proveedores,
        "movimientos_por_producto": movimientos_por_producto,
        "producto_form": producto_form,
        "proveedor_form": proveedor_form,
        "movimiento_form": movimiento_form,
        "fecha_inicio": fecha_inicio or "",
        "fecha_fin": fecha_fin or "",
        "producto_id": producto_id or "",
        "tipo_mov": tipo_mov or "",
    }

    return render(request, "almacen/almacen_dashboard.html", context)


# ------------------------------------------------------
# FUNCIÓN AUXILIAR: Exportar CSV
# ------------------------------------------------------
def export_movimientos_csv(movimientos):
    """
    Exporta los movimientos filtrados a un archivo CSV.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="movimientos_{datetime.date.today()}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Producto', 'Tipo', 'Cantidad', 'Proveedor', 'Fecha', 'Precio Unitario', 'Valor Total'])
    for m in movimientos:
        writer.writerow([
            m.producto.nombre,
            m.get_tipo_display(),
            m.cantidad,
            m.proveedor.nombre if m.proveedor else "-",
            m.fecha,
            m.precio_unitario,
            m.valor_total()
        ])

    return response
