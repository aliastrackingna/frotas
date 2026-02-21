from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db import models, transaction
from django.utils import timezone
from datetime import datetime
import random
from .models import Veiculo, Motorista, SolicitacaoMotorista, SolicitacaoViagem


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


def solicitacao_list(request):
    solicitacoes = SolicitacaoMotorista.objects.all()
    return render(request, 'solicitacao_list.html', {'solicitacoes': solicitacoes})


def solicitacao_detail(request, pk):
    solicitacao = get_object_or_404(SolicitacaoMotorista, pk=pk)
    return render(request, 'solicitacao_detail.html', {'solicitacao': solicitacao})


def solicitacao_gerenciar(request, pk):
    solicitacao = get_object_or_404(SolicitacaoMotorista, pk=pk)
    motoristas_disponiveis = get_motoristas_disponiveis(
        solicitacao.data_inicio, 
        solicitacao.data_fim_prevista
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'atribuir_motorista':
            motoristah_id = request.POST.get('motorista')
            if motoristah_id:
                solicitacao.motorista_id = motoristah_id
                if solicitacao.status == 'Pendente':
                    solicitacao.status = 'Confirmada'
                solicitacao.save()
                return redirect('solicitacao_detail', pk=pk)
        
        elif action == 'cancelar':
            solicitacao.status = 'Cancelada'
            solicitacao.save()
            return redirect('solicitacao_detail', pk=pk)
        
        elif action == 'confirmar':
            solicitacao.status = 'Confirmada'
            solicitacao.save()
            return redirect('solicitacao_detail', pk=pk)
        
        elif action == 'concluir':
            solicitacao.status = 'Concluida'
            solicitacao.save()
            return redirect('solicitacao_detail', pk=pk)
    
    return render(request, 'solicitacao_gerenciar.html', {
        'solicitacao': solicitacao,
        'motoristas': motoristas_disponiveis
    })


def get_motoristas_disponiveis(data_inicio, data_fim):
    ocupados = SolicitacaoMotorista.objects.filter(
        status__in=['Confirmada', 'Pendente']
    ).filter(
        models.Q(data_inicio__lt=data_fim, data_fim_prevista__gt=data_inicio)
    ).exclude(
        motorista__isnull=True
    ).values_list('motorista_id', flat=True)
    
    return Motorista.objects.exclude(id_motorista__in=ocupados)


@transaction.atomic
def solicitacao_create(request):
    if request.method == 'POST':
        data_inicio_str = request.POST.get('data_inicio')
        data_fim_str = request.POST.get('data_fim_prevista')
        observacao = request.POST.get('observacao', '')
        
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%dT%H:%M')
            data_inicio = timezone.make_aware(data_inicio)
            
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%dT%H:%M')
            data_fim = timezone.make_aware(data_fim)
        except (ValueError, TypeError):
            return render(request, 'solicitacao_form.html', {
                'error': 'Datas inválidas. Use o formato correto.'
            })
        
        if data_inicio < timezone.now():
            return render(request, 'solicitacao_form.html', {
                'error': 'A data de início não pode ser no passado.'
            })
        
        if data_fim <= data_inicio:
            return render(request, 'solicitacao_form.html', {
                'error': 'A data de retorno deve ser posterior à data de início.'
            })
        
        with transaction.atomic():
            solicitacao = SolicitacaoMotorista.objects.create(
                data_inicio=data_inicio,
                data_fim_prevista=data_fim,
                observacao=observacao,
                status='Pendente'
            )
            
            disponibilidade = get_motoristas_disponiveis(data_inicio, data_fim)
            lista_disponiveis = list(disponibilidade)
            
            if lista_disponiveis:
                random.seed()
                motorista_escolhido = random.choice(lista_disponiveis)
                solicitacao.motorista = motorista_escolhido
                solicitacao.status = 'Confirmada'
                solicitacao.save()
                return redirect('solicitacao_detail', pk=solicitacao.pk)
            else:
                solicitacao.status = 'Pendente'
                solicitacao.save()
                return render(request, 'solicitacao_form.html', {
                    'error': 'Nenhum motorista disponível neste horário. A solicitação ficou pendente.',
                    'success': True
                })
    
    return render(request, 'solicitacao_form.html', {})


def get_veiculos_disponiveis(data_inicio, data_fim, quantidade_passageiros):
    ocupados = SolicitacaoViagem.objects.filter(
        status__in=['Confirmada', 'Pendente']
    ).filter(
        models.Q(data_viagem__lt=data_fim, data_fim_prevista__gt=data_inicio)
    ).exclude(
        veiculo__isnull=True
    ).values_list('veiculo_id', flat=True)
    
    return Veiculo.objects.exclude(id_veiculo__in=ocupados).filter(
        quantidade_passageiros__gte=quantidade_passageiros
    )


def get_motoristas_disponiveis_viagem(data_inicio, data_fim):
    ocupados_motorista = SolicitacaoViagem.objects.filter(
        status__in=['Confirmada', 'Pendente']
    ).filter(
        models.Q(data_viagem__lt=data_fim, data_fim_prevista__gt=data_inicio)
    ).exclude(
        motorista__isnull=True
    ).values_list('motorista_id', flat=True)
    
    return Motorista.objects.exclude(id_motorista__in=ocupados_motorista)


def solicitacao_viagem_list(request):
    solicitacoes = SolicitacaoViagem.objects.all()
    return render(request, 'solicitacao_viagem_list.html', {'solicitacoes': solicitacoes})


def solicitacao_viagem_detail(request, pk):
    solicitacao = get_object_or_404(SolicitacaoViagem, pk=pk)
    return render(request, 'solicitacao_viagem_detail.html', {'solicitacao': solicitacao})


def solicitacao_viagem_gerenciar(request, pk):
    solicitacao = get_object_or_404(SolicitacaoViagem, pk=pk)
    veiculos_disponiveis = get_veiculos_disponiveis(
        solicitacao.data_viagem, 
        solicitacao.data_fim_prevista,
        solicitacao.quantidade_passageiros
    )
    motoristas_disponiveis = get_motoristas_disponiveis_viagem(
        solicitacao.data_viagem, 
        solicitacao.data_fim_prevista
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'atribuir_veiculo':
            veiculo_id = request.POST.get('veiculo')
            if veiculo_id:
                solicitacao.veiculo_id = veiculo_id
                if solicitacao.status == 'Pendente' and solicitacao.motorista:
                    solicitacao.status = 'Confirmada'
                solicitacao.save()
                return redirect('solicitacao_viagem_detail', pk=pk)
        
        elif action == 'atribuir_motorista':
            motoristah_id = request.POST.get('motorista')
            if motoristah_id:
                solicitacao.motorista_id = motoristah_id
                if solicitacao.status == 'Pendente' and solicitacao.veiculo:
                    solicitacao.status = 'Confirmada'
                solicitacao.save()
                return redirect('solicitacao_viagem_detail', pk=pk)
        
        elif action == 'cancelar':
            solicitacao.status = 'Cancelada'
            solicitacao.save()
            return redirect('solicitacao_viagem_detail', pk=pk)
        
        elif action == 'confirmar':
            solicitacao.status = 'Confirmada'
            solicitacao.save()
            return redirect('solicitacao_viagem_detail', pk=pk)
        
        elif action == 'concluir':
            solicitacao.status = 'Concluida'
            solicitacao.save()
            return redirect('solicitacao_viagem_detail', pk=pk)
    
    return render(request, 'solicitacao_viagem_gerenciar.html', {
        'solicitacao': solicitacao,
        'veiculos': veiculos_disponiveis,
        'motoristas': motoristas_disponiveis
    })


@transaction.atomic
def solicitacao_viagem_create(request):
    if request.method == 'POST':
        data_viagem_str = request.POST.get('data_viagem')
        data_fim_str = request.POST.get('data_fim_prevista')
        quantidade_passageiros = request.POST.get('quantidade_passageiros')
        local_embarque = request.POST.get('local_embarque')
        local_desembarque = request.POST.get('local_desembarque')
        observacao = request.POST.get('observacao', '')
        
        itinerario = []
        locais = request.POST.getlist('itinerario[]')
        for local in locais:
            if local.strip():
                itinerario.append(local.strip())
        
        try:
            data_viagem = datetime.strptime(data_viagem_str, '%Y-%m-%dT%H:%M')
            data_viagem = timezone.make_aware(data_viagem)
            
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%dT%H:%M')
            data_fim = timezone.make_aware(data_fim)
        except (ValueError, TypeError):
            return render(request, 'solicitacao_viagem_form.html', {
                'error': 'Datas inválidas. Use o formato correto.'
            })
        
        if data_viagem < timezone.now():
            return render(request, 'solicitacao_viagem_form.html', {
                'error': 'A data da viagem não pode ser no passado.'
            })
        
        if data_fim <= data_viagem:
            return render(request, 'solicitacao_viagem_form.html', {
                'error': 'A data de retorno deve ser posterior à data da viagem.'
            })
        
        with transaction.atomic():
            solicitacao = SolicitacaoViagem.objects.create(
                data_viagem=data_viagem,
                data_fim_prevista=data_fim,
                quantidade_passageiros=quantidade_passageiros,
                local_embarque=local_embarque,
                local_desembarque=local_desembarque,
                itinerario=itinerario,
                observacao=observacao,
                status='Pendente'
            )
            
            veiculos_disp = get_veiculos_disponiveis(data_viagem, data_fim, quantidade_passageiros)
            lista_veiculos = list(veiculos_disp)
            
            motoristas_disp = get_motoristas_disponiveis_viagem(data_viagem, data_fim)
            lista_motoristas = list(motoristas_disp)
            
            if lista_veiculos and lista_motoristas:
                random.seed()
                veiculo_escolhido = random.choice(lista_veiculos)
                motorista_escolhido = random.choice(lista_motoristas)
                
                solicitacao.veiculo = veiculo_escolhido
                solicitacao.motorista = motorista_escolhido
                solicitacao.status = 'Confirmada'
                solicitacao.save()
                return redirect('solicitacao_viagem_detail', pk=solicitacao.pk)
            else:
                erro_msg = ''
                if not lista_veiculos:
                    erro_msg += 'Nenhum veículo disponível com essa capacidade. '
                if not lista_motoristas:
                    erro_msg += 'Nenhum motorista disponível neste horário.'
                solicitacao.status = 'Pendente'
                solicitacao.save()
                return render(request, 'solicitacao_viagem_form.html', {
                    'error': erro_msg.strip() + ' A solicitação ficou pendente.',
                    'success': True
                })
    
    return render(request, 'solicitacao_viagem_form.html', {})
