from django.shortcuts import render, redirect
from .forms import TransaccionForm
from .models import Transaccion

def terminal_pagos_view(request):
    if request.method == 'POST':
        form = TransaccionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('terminal_pagos')
    else:
        form = TransaccionForm()

    transacciones = Transaccion.objects.order_by('-fecha_ingreso')[:10]

    return render(request, 'terminal_pagos/terminal.html', {
        'form': form,
        'transacciones': transacciones
    })
