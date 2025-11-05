from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.html import escape
from .models import Cliente
from .forms import ClienteForm

def clientes_view(request, pk=None):
    # 🔹 Si es AJAX GET con pk → devolver datos del cliente para editar
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

        # 🔹 Si es AJAX GET sin pk → devolver solo la tabla renderizada como texto
        clientes = Cliente.objects.all().order_by('nombre')
        html = ""
        for c in clientes:
            html += f"""
            <tr id='cliente-{c.id}'>
                <td>{escape(c.cedula)}</td>
                <td>{escape(c.nombre)}</td>
                <td>{escape(c.nacionalidad or '—')}</td>
                <td>{escape(c.direccion or '—')}</td>
                <td>{escape(c.telefono or '—')}</td>
                <td>{escape(c.referencia_1 or '—')}</td>
                <td>{escape(c.telefono_ref_1 or '—')}</td>
                <td>{escape(c.referencia_2 or '—')}</td>
                <td>{escape(c.telefono_ref_2 or '—')}</td>
                <td><span class="badge {'bg-success' if c.tipo == 'inversionista' else 'bg-secondary'}">{c.get_tipo_display()}</span></td>
                <td><span class="badge {'bg-danger' if c.status == 'lista_negra' else 'bg-primary'}">{c.get_status_display()}</span></td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="editarCliente({c.id})">✏️ Editar</button>
                </td>
            </tr>
            """
        if not html:
            html = "<tr><td colspan='12' class='text-center text-muted'>No hay clientes registrados.</td></tr>"
        return JsonResponse({'html': html})

    # 🔹 POST → crear o actualizar cliente
    if request.method == 'POST':
        cliente = get_object_or_404(Cliente, pk=pk) if pk else None
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})

    # 🔹 GET normal → render completo de la página
    clientes = Cliente.objects.all().order_by('nombre')
    form = ClienteForm()
    return render(request, 'clientes/clientes.html', {'clientes': clientes, 'form': form})
