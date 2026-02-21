from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Veiculo, Motorista


def index(request):
    total_veiculos = Veiculo.objects.count()
    return render(request, 'index.html', {'total_veiculos': total_veiculos})


def veiculo_list(request):
    veiculos = Veiculo.objects.all()
    return render(request, 'vehicles/veiculo_list.html', {'veiculos': veiculos})


def veiculo_detail(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    return render(request, 'vehicles/veiculo_detail.html', {'veiculo': veiculo})


def veiculo_create(request):
    if request.method == 'POST':
        placa = request.POST['placa']
        marca = request.POST['marca']
        quantidade_passageiros = request.POST['quantidade_passageiros']
        km_inicial = request.POST.get('km_inicial', 0)
        kms_atual = request.POST.get('kms_atual', 0)
        Veiculo.objects.create(
            placa=placa,
            marca=marca,
            quantidade_passageiros=quantidade_passageiros,
            km_inicial=km_inicial,
            kms_atual=kms_atual
        )
        return redirect('veiculo_list')
    return render(request, 'vehicles/veiculo_form.html', {})


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


def veiculo_delete(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    if request.method == 'POST':
        veiculo.delete()
        return redirect('veiculo_list')
    return render(request, 'vehicles/veiculo_confirm_delete.html', {'veiculo': veiculo})


def observacao_create(request, veiculo_pk):
    veiculo = get_object_or_404(Veiculo, pk=veiculo_pk)
    if request.method == 'POST':
        texto = request.POST.get('texto', '').strip()
        if texto:
            veiculo.observacoes.create(texto=texto)
    return redirect('veiculo_detail', pk=veiculo_pk)


def motoristah_list(request):
    motores = Motorista.objects.all()
    return render(request, 'motorista_list.html', {'motoristas': motores})


def motoristah_detail(request, pk):
    motorista = get_object_or_404(Motorista, pk=pk)
    return render(request, 'motorista_detail.html', {'motorista': motorista})


def motoristah_create(request):
    if request.method == 'POST':
        nome = request.POST['nome']
        tipo_carteira = request.POST['tipo_carteira']
        Motorista.objects.create(nome=nome, tipo_carteira=tipo_carteira)
        return redirect('motorista_list')
    return render(request, 'motorista_form.html', {})


def motoristah_update(request, pk):
    motoristah = get_object_or_404(Motorista, pk=pk)
    if request.method == 'POST':
        motoristah.nome = request.POST['nome']
        motoristah.tipo_carteira = request.POST['tipo_carteira']
        motoristah.save()
        return redirect('motorista_list')
    return render(request, 'motorista_form.html', {'motorista': motoristah})


def motoristah_delete(request, pk):
    motoristah = get_object_or_404(Motorista, pk=pk)
    if request.method == 'POST':
        motoristah.delete()
        return redirect('motorista_list')
    return render(request, 'motorista_confirm_delete.html', {'motorista': motoristah})
