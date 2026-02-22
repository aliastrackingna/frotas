from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
import random
from ..models import SolicitacaoViagem, SolicitacaoMotorista
from .utils import (
    get_veiculos_disponiveis, 
    get_motoristas_disponiveis,
    _parse_datetime, 
    _validar_datas, 
    _processar_action_gerenciar
)


@login_required
def solicitacao_viagem_list(request):
    data_inicio_pesquisa = request.GET.get('data_inicio')
    data_fim_pesquisa = request.GET.get('data_fim')
    
    filtros = {}
    
    # Se o usuário preencheu a data INICIAL da pesquisa
    # A viagem deve ter terminado DEPOIS ou NO MESMO DIA dessa data
    if data_inicio_pesquisa:
        filtros['data_fim_prevista__date__gte'] = data_inicio_pesquisa
        
    # Se o usuário preencheu a data FINAL da pesquisa
    # A viagem deve ter começado ANTES ou NO MESMO DIA dessa data
    if data_fim_pesquisa:
        filtros['data_viagem__date__lte'] = data_fim_pesquisa

    # Executa a query com os filtros combinados (lógica AND)
    # Graças à Lazy Evaluation do Django, isso gera apenas um SELECT no banco
    solicitacoes = SolicitacaoViagem.objects.filter(**filtros).select_related('veiculo', 'solicitacao_motorista')
    
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    return render(request, 'solicitacao_viagem_list.html', {
        'solicitacoes': solicitacoes,
        'data_inicio': data_inicio_pesquisa,
        'data_fim': data_fim_pesquisa,
        'today': today,
        'tomorrow': tomorrow
    })


@login_required
def solicitacao_viagem_detail(request, pk):
    solicitacao = get_object_or_404(
        SolicitacaoViagem.objects.select_related('veiculo', 'solicitacao_motorista__motorista'),
        pk=pk
    )
    return render(request, 'solicitacao_viagem_detail.html', {'solicitacao': solicitacao})


@login_required
def solicitacao_viagem_gerenciar(request, pk):
    solicitacao = get_object_or_404(
        SolicitacaoViagem.objects.select_related('veiculo', 'solicitacao_motorista'),
        pk=pk
    )
    veiculos_disponiveis = get_veiculos_disponiveis(
        solicitacao.data_viagem, 
        solicitacao.data_fim_prevista,
        solicitacao.quantidade_passageiros
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        veiculo_id = request.POST.get('veiculo')
        solicitacao_motorista_id = request.POST.get('solicitacao_motorista')
        
        if _processar_action_gerenciar(solicitacao, action, veiculo_id=veiculo_id, solicitacao_motorista_id=solicitacao_motorista_id):
            return redirect('solicitacao_viagem_detail', pk=pk)
    
    solicitacoes_motorista = SolicitacaoMotorista.objects.filter(
        data_inicio__lte=solicitacao.data_fim_prevista,
        data_fim_prevista__gte=solicitacao.data_viagem,
        status__in=['Pendente', 'Confirmada']
    ).select_related('motorista')
    
    return render(request, 'solicitacao_viagem_gerenciar.html', {
        'solicitacao': solicitacao,
        'veiculos': list(veiculos_disponiveis),
        'solicitacoes_motorista': list(solicitacoes_motorista)
    })


@login_required
@transaction.atomic
def solicitacao_viagem_create(request):
    if request.method == 'POST':
        data_viagem_data = request.POST.get('data_viagem_data')
        data_viagem_hora = request.POST.get('data_viagem_hora')
        data_fim_data = request.POST.get('data_fim_prevista_data')
        data_fim_hora = request.POST.get('data_fim_prevista_hora')
        
        if not data_viagem_data or not data_viagem_hora:
            return render(request, 'solicitacao_viagem_form.html', {'error': 'Data e hora da viagem são obrigatórios.'})
        
        if not data_fim_data or not data_fim_hora:
            return render(request, 'solicitacao_viagem_form.html', {'error': 'Data e hora de retorno são obrigatórios.'})
        
        data_viagem_str = f"{data_viagem_data} {data_viagem_hora}"
        data_fim_str = f"{data_fim_data} {data_fim_hora}"
        
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
            
            if lista_veiculos:
                random.seed()
                solicitacao.veiculo = lista_veiculos[0]

                capacidade = solicitacao.veiculo.quantidade_passageiros
                lugares_vazios = capacidade - quantidade_passageiros
                
                if quantidade_passageiros >= 23:
                    solicitacao.observacao = 'Alocado automaticamente para veículo de grande porte.'
                elif lugares_vazios > 4: 
                    solicitacao.status = 'Pendente'
                    solicitacao.observacao = f'Alerta de ociosidade: Solicitado para {quantidade_passageiros}, mas o menor veículo disponível tem {capacidade} lugares. Requer autorização do coordenador.'
                    return render(request, 'solicitacao_viagem_form.html', {
                        'error': f' {solicitacao.observacao} A solicitação ficou pendente.',
                        'success': False
                    })
                
                motoristas_disp = get_motoristas_disponiveis(data_viagem, data_fim)
                if motoristas_disp.exists():
                    primeiro_motorista = random.choice(list(motoristas_disp))
                    solicitacao_motorista = SolicitacaoMotorista.objects.create(
                        data_inicio=data_viagem,
                        data_fim_prevista=data_fim,
                        motorista=primeiro_motorista,
                        status='Confirmada'
                    )
                    solicitacao.solicitacao_motorista = solicitacao_motorista
                        
                    solicitacao.status = 'Confirmada'
                else:
                    solicitacao.status = 'Pendente'
                    return render(request, 'solicitacao_viagem_form.html', {
                        'error': 'A solicitação ficou pendente.\nNenhum motorista disponível',
                        'success': False
                    })
                
                solicitacao.save()
                return redirect('solicitacao_viagem_detail', pk=solicitacao.pk)
            else:
                errors = []
                if not lista_veiculos:
                    errors.append('Nenhum veículo disponível com essa capacidade.')
                
                solicitacao.status = 'Pendente'
                solicitacao.save()
                return render(request, 'solicitacao_viagem_form.html', {
                    'error': ' '.join(errors) + ' A solicitação ficou pendente.',
                    'success': True
                })
    
    return render(request, 'solicitacao_viagem_form.html')
