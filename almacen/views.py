from django.shortcuts import render, redirect
from django.db.models import Sum, Q
from django.http import HttpResponse
from django.contrib import messages
from .models import Producto, Proveedor, Movimiento
from .forms import ProductoForm, ProveedorForm, MovimientoForm
import datetime
import csv
import openpyxl
import openpyxl
from openpyxl.styles import Font
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json 

def almacen_dashboard(request):
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
        # Crear producto individual
        if 'producto_submit' in request.POST:
            producto_form = ProductoForm(request.POST)
            if producto_form.is_valid():
                producto_form.save()
                messages.success(request, "Producto creado correctamente.")
                return redirect('almacen_dashboard')

        # Crear proveedor
        elif 'proveedor_submit' in request.POST:
            proveedor_form = ProveedorForm(request.POST)
            if proveedor_form.is_valid():
                proveedor_form.save()
                messages.success(request, "Proveedor creado correctamente.")
                return redirect('almacen_dashboard')

        # Crear movimiento
        elif 'movimiento_submit' in request.POST:
            movimiento_form = MovimientoForm(request.POST)
            if movimiento_form.is_valid():
                movimiento_form.save()
                messages.success(request, "Movimiento registrado correctamente.")
                return redirect('almacen_dashboard')

        # Exportar CSV
        elif 'export_csv' in request.POST:
            return export_movimientos_csv(movimientos)

        # Carga masiva de factura (solo crea movimientos para productos existentes)
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

            expected_headers = ['referencia', 'cantidad', 'precio_unitario', 'proveedor', 'factura_referencia']
            actual_headers = [str(cell.value).strip().lower() for cell in ws[1] if cell.value]
            if actual_headers != expected_headers:
                messages.error(request, f"Encabezados inválidos. Se esperaban: {expected_headers}")
                return redirect('almacen_dashboard')

            movimientos_creados = 0
            productos_no_existentes = []
            errores = []

            for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                referencia, cantidad, precio_unitario, proveedor_nombre, factura_ref = row

                # Validaciones básicas
                if not referencia or cantidad is None or precio_unitario is None:
                    errores.append(f"Fila {i}: campos obligatorios vacíos.")
                    continue

                try:
                    cantidad = int(cantidad)
                    precio_unitario = float(precio_unitario)
                except ValueError:
                    errores.append(f"Fila {i}: cantidad o precio_unitario inválido.")
                    continue

                # Buscar producto existente
                producto = Producto.objects.filter(referencia=str(referencia).strip()).first()

                if not producto:
                    productos_no_existentes.append({
                        "fila": i,
                        "referencia": referencia,
                        "factura_ref": factura_ref
                    })
                    continue

                # Buscar o crear proveedor
                proveedor = None
                if proveedor_nombre:
                    proveedor, _ = Proveedor.objects.get_or_create(nombre=str(proveedor_nombre).strip())

                # Crear el movimiento
                Movimiento.objects.create(
                    producto=producto,
                    tipo='ingreso_compra',
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    proveedor=proveedor
                )
                movimientos_creados += 1

            # ---------------------------
            # Generar log de productos no admitidos
            # ---------------------------
            if productos_no_existentes:
                log_wb = openpyxl.Workbook()
                log_ws = log_wb.active
                log_ws.title = "No encontrados"
                log_ws.append(["Fila", "Referencia", "Factura Referencia"])
                for prod in productos_no_existentes:
                    log_ws.append([prod["fila"], prod["referencia"], prod["factura_ref"]])

                for cell in log_ws[1]:
                    cell.font = Font(bold=True)

                response = HttpResponse(
                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                response["Content-Disposition"] = 'attachment; filename="productos_no_encontrados.xlsx"'
                log_wb.save(response)
                return response

            # ---------------------------
            # Mensajes finales
            # ---------------------------
            if errores:
                messages.warning(request, f"Se encontraron algunos errores: {errores}")
            if movimientos_creados:
                messages.success(request, f"Se crearon {movimientos_creados} movimientos correctamente.")
            if not movimientos_creados and not productos_no_existentes:
                messages.info(request, "No se creó ningún movimiento.")

            return redirect('almacen_dashboard')


        # Carga masiva de factura de proveedor (movimientos)
        elif 'carga_masiva_factura' in request.POST:
            archivo = request.FILES.get('archivo_factura')
            if not archivo:
                messages.error(request, "Debe seleccionar un archivo de factura.")
                return redirect('almacen_dashboard')

            try:
                wb = openpyxl.load_workbook(archivo)
                ws = wb.active
            except Exception as e:
                messages.error(request, f"No se pudo leer el archivo: {str(e)}")
                return redirect('almacen_dashboard')

            # Validar encabezados
            expected_headers = ['referencia', 'cantidad', 'precio_unitario', 'proveedor']
            actual_headers = [str(cell.value).strip().lower() for cell in ws[1] if cell.value]
            if actual_headers != expected_headers:
                messages.error(request, f"Encabezados inválidos. Se esperaban: {expected_headers}")
                return redirect('almacen_dashboard')

            movimientos_creados = 0
            errores = []

            for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                ref, cantidad, precio_unitario, proveedor_nombre = row

                # Validación de campos obligatorios
                if not ref or cantidad is None or precio_unitario is None:
                    errores.append(f"Fila {i}: campos obligatorios vacíos.")
                    continue

                # Conversión de valores numéricos
                try:
                    cantidad = int(cantidad)
                    precio_unitario = float(precio_unitario)
                except ValueError:
                    errores.append(f"Fila {i}: cantidad o precio_unitario inválido.")
                    continue

                # 🔍 Buscar producto por referencia o por nombre
                producto = Producto.objects.filter(referencia=ref).first()
                if not producto:
                    producto = Producto.objects.filter(nombre__icontains=ref).first()

                if not producto:
                    errores.append(f"Fila {i}: no se encontró producto con referencia o nombre '{ref}'.")
                    continue

                # Buscar o crear proveedor
                proveedor = None
                if proveedor_nombre:
                    proveedor, _ = Proveedor.objects.get_or_create(nombre=str(proveedor_nombre).strip())

                # Crear el movimiento
                Movimiento.objects.create(
                    producto=producto,
                    tipo='ingreso_compra',
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    proveedor=proveedor
                )
                movimientos_creados += 1

            # Reportar resultados
            if errores:
                messages.error(request, f"Errores en algunas filas: {errores}")
            if movimientos_creados:
                messages.success(request, f"Se crearon {movimientos_creados} movimientos correctamente.")

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

def editar_producto(request, id):
    """Actualiza los datos de un producto en tiempo real (AJAX)."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            producto = Producto.objects.get(pk=id)

            producto.nombre = data.get("nombre", producto.nombre)
            producto.referencia = data.get("referencia", producto.referencia)
            producto.utilidad = data.get("utilidad", producto.utilidad)
            producto.precio_venta = data.get("precio_venta", producto.precio_venta)
            producto.ean = data.get("ean", producto.ean)
            producto.save()

            return JsonResponse({"success": True})
        except Producto.DoesNotExist:
            return JsonResponse({"success": False, "error": "Producto no encontrado."}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": False, "error": "Método no permitido."}, status=405)
