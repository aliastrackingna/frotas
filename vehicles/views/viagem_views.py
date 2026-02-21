from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from datetime import datetime, timedelta
import random
from ..models import SolicitacaoViagem
from .utils import (
    get_veiculos_disponiveis, 
    get_motoristas_disponiveis_viagem, 
    _parse_datetime, 
    _validar_datas, 
    _processar_action_gerenciar
)


def solicitacao_viagem_list(request):
    solicitacoes = SolicitacaoViagem.objects.all()
    
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    if data_inicio:
        solicitacoes = solicitacoes.filter(data_viagem__date__gte=data_inicio)
    if data_fim:
        solicitacoes = solicitacoes.filter(data_viagem__date__lte=data_fim)
    
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    return render(request, 'solicitacao_viagem_list.html', {
        'solicitacoes': solicitacoes,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'today': today,
        'tomorrow': tomorrow
    })


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
        veiculo_id = request.POST.get('veiculo')
        motoristal_id = request.POST.get('motorista')
        
        if _processar_action_gerenciar(solicitacao, action, veiculo_id, motoristal_id):
            return redirect('solicitacao_viagem_detail', pk=pk)
    
    return render(request, 'solicitacao_viagem_gerenciar.html', {
        'solicitacao': solicitacao,
        'veiculos': list(veiculos_disponiveis),
        'motoristas': list(motoristas_disponiveis)
    })


@transaction.atomic
def solicitacao_viagem_create(request):
    if request.method == 'POST':
        data_viagem_str = request.POST.get('data_viagem')
        data_fim_str = request.POST.get('data_fim_prevista')
        
        data_viagem, error = _parse_datetime(data_viagem_str)
        if error:
            return render(request, 'solicitacao_viagem_form.html', {'error': error})
        
        data_fim, error = _parse_datetime(data_fim_str)
        if error:
            return render(request, 'solicitacao_viagem_form.html', {'error': error})
        
        error = _validar_datas(data_viagem, data_fim)
        if error:
            return render(request, 'solicitacao_viagem_form.html', {'error': error})
        
        itinerario = [loc.strip() for loc in request.POST.getlist('itinerario[]') if loc.strip()]
        quantidade_passageiros = int(request.POST.get('quantidade_passageiros', 1))
        
        with transaction.atomic():
            solicitacao = SolicitacaoViagem.objects.create(
                data_viagem=data_viagem,
                data_fim_prevista=data_fim,
                quantidade_passageiros=quantidade_passageiros,
                local_embarque=request.POST.get('local_embarque'),
                local_desembarque=request.POST.get('local_desembarque'),
                itinerario=itinerario,
                observacao=request.POST.get('observacao', ''),
                status='Pendente'
            )
            
            veiculos_disp = get_veiculos_disponiveis(data_viagem, data_fim, quantidade_passageiros)
            lista_veiculos = list(veiculos_disp)
            
            motoristas_disp = get_motoristas_disponiveis_viagem(data_viagem, data_fim)
            lista_motoristas = list(motoristas_disp)
            
            if lista_veiculos and lista_motoristas:
                random.seed()
                solicitacao.veiculo = lista_veiculos[0]
                solicitacao.motorista = random.choice(lista_motoristas)

                capacidade = solicitacao.veiculo.quantidade_passageiros
                
                if quantidade_passageiros >= 23:
                    solicitacao.status = 'Confirmada'
                    solicitacao.observacao = 'Alocado automaticamente para veículo de grande porte.'
                
                else:
                    lugares_vazios = capacidade - quantidade_passageiros
                    if lugares_vazios > 4: 
                        solicitacao.status = 'Pendente'
                        solicitacao.observacao = f'Alerta de ociosidade: Solicitado para {quantidade_passageiros}, mas o menor veículo disponível tem {capacidade} lugares. Requer autorização do coordenador.'
                    else:
                        solicitacao.status = 'Confirmada'
                        solicitacao.observacao = 'Veículo alocado com eficiência.'
                solicitacao.save()
                return redirect('solicitacao_viagem_detail', pk=solicitacao.pk)
            else:
                errors = []
                if not lista_veiculos:
                    errors.append('Nenhum veículo disponível com essa capacidade.')
                if not lista_motoristas:
                    errors.append('Nenhum motorista disponível neste horário.')
                
                solicitacao.status = 'Pendente'
                solicitacao.save()
                return render(request, 'solicitacao_viagem_form.html', {
                    'error': ' '.join(errors) + ' A solicitação ficou pendente.',
                    'success': True
                })
    
    return render(request, 'solicitacao_viagem_form.html')
