from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Cliente
from .forms import ClienteForm

def clientes_view(request, pk=None):
    # Si es AJAX y GET → obtener datos del cliente para editar
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'GET':
        if pk:
            cliente = get_object_or_404(Cliente, pk=pk)
            data = {
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
            return JsonResponse(data)
        return JsonResponse({'error': 'Cliente no encontrado'}, status=404)

    # POST → crear o actualizar cliente
    if request.method == 'POST':
        cliente = get_object_or_404(Cliente, pk=pk) if pk else None
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})

    # GET normal → render de la lista
    clientes = Cliente.objects.all().order_by('nombre')
    form = ClienteForm()
    return render(request, 'clientes/clientes.html', {'clientes': clientes, 'form': form})
