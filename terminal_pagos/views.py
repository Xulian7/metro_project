from django.shortcuts import render, redirect
from .forms import TransaccionForm
from .models import Transaccion
from django.utils import timezone

def terminal_pagos_view(request):
    if request.method == 'POST':
        form = TransaccionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('terminal_pagos')  # recarga la misma página
    else:
        form = TransaccionForm(initial={'fecha_ingreso': timezone.now()})

    transacciones = Transaccion.objects.order_by('-fecha_ingreso')[:10]

    return render(request, 'terminal_pagos/terminal.html', {
        'form': form,
        'transacciones': transacciones
    })
