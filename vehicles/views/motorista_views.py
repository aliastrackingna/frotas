from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from ..models import Motorista


@login_required
def motorista_list(request):
    return render(request, 'motorista_list.html', {'motoristas': Motorista.objects.all()})


@login_required
def motorista_detail(request, pk):
    motorista = get_object_or_404(Motorista, pk=pk)
    return render(request, 'motorista_detail.html', {'motorista': motorista})


@login_required
def motorista_create(request):
    if request.method == 'POST':
        Motorista.objects.create(
            nome=request.POST['nome'],
            tipo_carteira=request.POST['tipo_carteira']
        )
        return redirect('motorista_list')
    return render(request, 'motorista_form.html')


@login_required
def motorista_update(request, pk):
    motorista = get_object_or_404(Motorista, pk=pk)
    if request.method == 'POST':
        motorista.nome = request.POST['nome']
        motorista.tipo_carteira = request.POST['tipo_carteira']
        motorista.save()
        return redirect('motorista_list')
    return render(request, 'motorista_form.html', {'motorista': motorista})


@login_required
def motorista_delete(request, pk):
    motorista = get_object_or_404(Motorista, pk=pk)
    if request.method == 'POST':
        motorista.delete()
        return redirect('motorista_list')
    return render(request, 'motorista_confirm_delete.html', {'motorista': motorista})
