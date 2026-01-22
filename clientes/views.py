from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages

from .models import Cliente
from .forms import ClienteForm


# ==========================================================
# DASHBOARD PRINCIPAL (listar y crear clientes)
# ==========================================================
def clientes_dashboard(request):
    clientes = Cliente.objects.all().order_by('nombre')
    form = ClienteForm()

    if request.method == "POST":
        # ========================
        # CREAR NUEVO CLIENTE
        # ========================
        if 'cliente_submit' in request.POST:
            form = ClienteForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "🐾 Cliente creado correctamente.")
                return redirect('clientes_dashboard')
            else:
                messages.error(request, "⚠️ Revisa los datos del formulario.")

    context = {
        'clientes': clientes,
        'form': form,
    }
    return render(request, "clientes/clientes_dashboard.html", context)


# ==========================================================
# ACTUALIZAR CLIENTE (AJAX / MODAL)
# ==========================================================
def cliente_update(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Método no permitido.')

    cliente_id = request.POST.get('cliente_id')
    if not cliente_id:
        return HttpResponseBadRequest('Falta el ID del cliente.')

    cliente = get_object_or_404(Cliente, id=cliente_id)

    # 🔑 USAR EL FORM (no asignaciones manuales)
    form = ClienteForm(request.POST, instance=cliente)

    if not form.is_valid():
        return JsonResponse({
            'status': 'error',
            'errors': form.errors,
        }, status=400)

    cliente = form.save()

    # ✅ Respuesta JSON para actualizar la tabla sin recargar
    return JsonResponse({
        'status': 'ok',
        'cliente': {
            'id': cliente.id,
            'cedula': cliente.cedula,
            'nombre': cliente.nombre,
            'nacionalidad': cliente.nacionalidad,
            'direccion': cliente.direccion,
            'telefono': cliente.telefono,
            'referencia_1': cliente.referencia_1,
            'telefono_ref_1': cliente.telefono_ref_1,
            'referencia_2': cliente.referencia_2,
            'telefono_ref_2': cliente.telefono_ref_2,
            'tipo': cliente.tipo,
            'status': cliente.status,

            # 👇 NUEVOS CAMPOS (solo si es Inversionista)
            'costo_operativo': cliente.costo_operativo,
            'costo_administrativo': cliente.costo_administrativo,
        }
    })
