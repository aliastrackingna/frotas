from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from ..models import Motorista


@login_required
def motorista_list(request):
    return render(request, 'motorista_list.html', {'motoristas': Motorista.objects.all()})


@login_required
def motorista_detail(request, pk):
    motoristal = get_object_or_404(Motorista, pk=pk)
    return render(request, 'motorista_detail.html', {'motorista': motoristal})


@login_required
def motoristal_create(request):
    if request.method == 'POST':
        Motorista.objects.create(
            nome=request.POST['nome'],
            tipo_carteira=request.POST['tipo_carteira']
        )
        return redirect('motorista_list')
    return render(request, 'motorista_form.html')


@login_required
def motoristal_update(request, pk):
    motoristal = get_object_or_404(Motorista, pk=pk)
    if request.method == 'POST':
        motoristal.nome = request.POST['nome']
        motoristal.tipo_carteira = request.POST['tipo_carteira']
        motoristal.save()
        return redirect('motorista_list')
    return render(request, 'motorista_form.html', {'motorista': motoristal})


@login_required
def motoristal_delete(request, pk):
    motoristal = get_object_or_404(Motorista, pk=pk)
    if request.method == 'POST':
        motoristal.delete()
        return redirect('motorista_list')
    return render(request, 'motorista_confirm_delete.html', {'motorista': motoristal})
