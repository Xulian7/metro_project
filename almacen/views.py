from django.shortcuts import render, redirect
from django.db.models import Sum, Q
from django.http import HttpResponse
from django.contrib import messages
from .models import Producto, Proveedor, Movimiento
from .forms import ProductoForm, ProveedorForm, MovimientoForm
import datetime
import csv
import openpyxl


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
        # ---------------------------
        # Crear producto individual
        # ---------------------------
        if 'producto_submit' in request.POST:
            producto_form = ProductoForm(request.POST)
            if producto_form.is_valid():
                producto_form.save()
                messages.success(request, "Producto creado correctamente.")
                return redirect('almacen_dashboard')

        # ---------------------------
        # Crear proveedor
        # ---------------------------
        elif 'proveedor_submit' in request.POST:
            proveedor_form = ProveedorForm(request.POST)
            if proveedor_form.is_valid():
                proveedor_form.save()
                messages.success(request, "Proveedor creado correctamente.")
                return redirect('almacen_dashboard')

        # ---------------------------
        # Crear movimiento
        # ---------------------------
        elif 'movimiento_submit' in request.POST:
            movimiento_form = MovimientoForm(request.POST)
            if movimiento_form.is_valid():
                movimiento_form.save()
                messages.success(request, "Movimiento registrado correctamente.")
                return redirect('almacen_dashboard')

        # ---------------------------
        # Exportar CSV
        # ---------------------------
        elif 'export_csv' in request.POST:
            return export_movimientos_csv(movimientos)

        # ---------------------------
        # Carga masiva de productos
        # ---------------------------
        elif 'carga_masiva_productos' in request.POST:
            archivo = request.FILES.get('archivo_excel')
            if not archivo:
                messages.error(request, "Debe seleccionar un archivo.")
                return redirect('almacen_dashboard')

            try:
                wb = openpyxl.load_workbook(archivo)
                ws = wb.active
            except Exception as e:
                messages.error(request, f"No se pudo leer el archivo: {str(e)}")
                return redirect('almacen_dashboard')

            # Validar encabezados
            expected_headers = ['referencia', 'nombre', 'precio_venta', 'utilidad', 'ean']
            actual_headers = [cell.value for cell in ws[1]]
            if actual_headers != expected_headers:
                messages.error(request, f"Encabezados inválidos. Se esperaban: {expected_headers}")
                return redirect('almacen_dashboard')

            productos_creados = 0
            errores = []

            for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                ref, nombre, precio, utilidad, ean = row

                # Validaciones básicas
                if not ref or not nombre or precio is None:
                    errores.append(f"Fila {i}: campos obligatorios vacíos")
                    continue

                try:
                    precio = float(precio)
                except ValueError:
                    errores.append(f"Fila {i}: precio_venta inválido")
                    continue

                # Crear o actualizar producto
                producto, created = Producto.objects.update_or_create(
                    referencia=ref,
                    defaults={
                        'nombre': nombre,
                        'precio_venta': precio,
                        'utilidad': utilidad,
                        'ean': ean
                    }
                )
                if created:
                    productos_creados += 1

            if errores:
                messages.error(request, f"Errores en algunas filas: {errores}")
            if productos_creados:
                messages.success(request, f"Se crearon {productos_creados} productos correctamente.")

            return redirect('almacen_dashboard')

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

    return render(request, "almacen/almacen_tree_stock.html", context)


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
