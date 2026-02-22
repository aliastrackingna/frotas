from django.shortcuts import render, get_object_or_404, redirect
from django.db import models
from django.contrib.auth.decorators import login_required
from ..models import Veiculo


@login_required
def index(request):
    total_veiculos = Veiculo.objects.count()
    return render(request, 'index.html', {'total_veiculos': total_veiculos})


@login_required
def veiculo_list(request):
    veiculos = Veiculo.objects.all()
    busca = request.GET.get('busca', '')
    if busca:
        veiculos = veiculos.filter(
            models.Q(placa__icontains=busca) |
            models.Q(marca__icontains=busca) |
            models.Q(modelo__icontains=busca)
        )
    return render(request, 'vehicles/veiculo_list.html', {
        'veiculos': veiculos,
        'busca': busca
    })


@login_required
def veiculo_detail(request, pk):
    veiculo = get_object_or_404(Veiculo.objects.prefetch_related('observacoes'), pk=pk)
    return render(request, 'vehicles/veiculo_detail.html', {'veiculo': veiculo})


@login_required
def veiculo_create(request):
    if request.method == 'POST':
        Veiculo.objects.create(
            placa=request.POST['placa'],
            marca=request.POST['marca'],
            quantidade_passageiros=request.POST['quantidade_passageiros'],
            km_inicial=request.POST.get('km_inicial', 0),
            kms_atual=request.POST.get('kms_atual', 0)
        )
        return redirect('veiculo_list')
    return render(request, 'vehicles/veiculo_form.html')


@login_required
def veiculo_update(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    if request.method == 'POST':
        veiculo.placa = request.POST['placa']
        veiculo.marca = request.POST['marca']
        veiculo.quantidade_passageiros = request.POST['quantidade_passageiros']
        veiculo.km_inicial = request.POST.get('km_inicial', 0)
        veiculo.kms_atual = request.POST.get('kms_atual', 0)
        veiculo.save()
        return redirect('veiculo_list')
    return render(request, 'vehicles/veiculo_form.html', {'veiculo': veiculo})


@login_required
def veiculo_delete(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    if request.method == 'POST':
        veiculo.delete()
        return redirect('veiculo_list')
    return render(request, 'vehicles/veiculo_confirm_delete.html', {'veiculo': veiculo})


@login_required
def observacao_create(request, veiculo_pk):
    veiculo = get_object_or_404(Veiculo, pk=veiculo_pk)
    if request.method == 'POST':
        texto = request.POST.get('texto', '').strip()
        if texto:
            veiculo.observacoes.create(texto=texto)
    return redirect('veiculo_detail', pk=veiculo_pk)
