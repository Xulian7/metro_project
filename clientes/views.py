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
# ACTUALIZAR CLIENTE (AJAX)
# ==========================================================
def cliente_update(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        if not cliente_id:
            return HttpResponseBadRequest('Falta el ID del cliente.')

        cliente = get_object_or_404(Cliente, id=cliente_id)

        # Actualizar campos
        cliente.cedula = request.POST.get('cedula')
        cliente.nombre = request.POST.get('nombre')
        cliente.nacionalidad = request.POST.get('nacionalidad')
        cliente.direccion = request.POST.get('direccion')
        cliente.telefono = request.POST.get('telefono')
        cliente.referencia_1 = request.POST.get('referencia_1')
        cliente.telefono_ref_1 = request.POST.get('telefono_ref_1')
        cliente.referencia_2 = request.POST.get('referencia_2')
        cliente.telefono_ref_2 = request.POST.get('telefono_ref_2')
        cliente.tipo = request.POST.get('tipo')
        cliente.status = request.POST.get('status')
        cliente.save()

        # Devolver JSON para actualizar tabla sin recargar
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
            }
        })

    return HttpResponseBadRequest('Método no permitido.')
