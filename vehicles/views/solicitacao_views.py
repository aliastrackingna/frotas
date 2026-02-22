from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
import random
from ..models import SolicitacaoMotorista
from .utils import get_motoristas_disponiveis, _parse_datetime, _validar_datas, _processar_action_gerenciar


@login_required
def solicitacao_list(request):
    data_inicio_pesquisa = request.GET.get('data_inicio')
    data_fim_pesquisa = request.GET.get('data_fim')
    
    filtros = {}
    
    if data_inicio_pesquisa:
        filtros['data_fim_prevista__date__gte'] = data_inicio_pesquisa
        
    if data_fim_pesquisa:
        filtros['data_inicio__date__lte'] = data_fim_pesquisa

    solicitacoes = SolicitacaoMotorista.objects.filter(**filtros).select_related('motorista')
    
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    return render(request, 'solicitacao_list.html', {
        'solicitacoes': solicitacoes,
        'data_inicio': data_inicio_pesquisa,
        'data_fim': data_fim_pesquisa,
        'today': today,
        'tomorrow': tomorrow
    })


@login_required
def solicitacao_detail(request, pk):
    solicitacao = get_object_or_404(SolicitacaoMotorista.objects.select_related('motorista'), pk=pk)
    return render(request, 'solicitacao_detail.html', {'solicitacao': solicitacao})


@login_required
def solicitacao_gerenciar(request, pk):
    solicitacao = get_object_or_404(SolicitacaoMotorista, pk=pk)
    motoresas_disponiveis = get_motoristas_disponiveis(
        solicitacao.data_inicio, solicitacao.data_fim_prevista
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        veiculo_id = None
        motoristal_id = request.POST.get('motorista')
        
        if _processar_action_gerenciar(solicitacao, action, veiculo_id=veiculo_id, motoristal_id=motoristal_id):
            return redirect('solicitacao_detail', pk=pk)
    
    return render(request, 'solicitacao_gerenciar.html', {
        'solicitacao': solicitacao,
        'motoristas': list(motoresas_disponiveis)
    })


@login_required
@transaction.atomic
def solicitacao_create(request):
    if request.method == 'POST':
        data_inicio_data = request.POST.get('data_inicio_data')
        data_inicio_hora = request.POST.get('data_inicio_hora')
        data_fim_data = request.POST.get('data_fim_prevista_data')
        data_fim_hora = request.POST.get('data_fim_prevista_hora')
        
        if not data_inicio_data or not data_inicio_hora:
            return render(request, 'solicitacao_form.html', {'error': 'Data e hora de início são obrigatórios.'})
        
        if not data_fim_data or not data_fim_hora:
            return render(request, 'solicitacao_form.html', {'error': 'Data e hora de retorno são obrigatórios.'})
        
        data_inicio_str = f"{data_inicio_data} {data_inicio_hora}"
        data_fim_str = f"{data_fim_data} {data_fim_hora}"
        
        data_inicio, error = _parse_datetime(data_inicio_str)
        if error:
            return render(request, 'solicitacao_form.html', {'error': error})
        
        data_fim, error = _parse_datetime(data_fim_str)
        if error:
            return render(request, 'solicitacao_form.html', {'error': error})
        
        error = _validar_datas(data_inicio, data_fim)
        if error:
            return render(request, 'solicitacao_form.html', {'error': error})

        with transaction.atomic():
            solicitacao = SolicitacaoMotorista.objects.create(
                data_inicio=data_inicio,
                data_fim_prevista=data_fim,
                observacao=request.POST.get('observacao', ''),
                status='Pendente'
            )
            
            disponibilidade = get_motoristas_disponiveis(data_inicio, data_fim)
            lista_disponiveis = list(disponibilidade)
            
            if lista_disponiveis:
                random.seed()
                solicitacao.motorista = random.choice(lista_disponiveis)
                solicitacao.status = 'Confirmada'
                solicitacao.save()
                return redirect('solicitacao_detail', pk=solicitacao.pk)
            else:
                solicitacao.status = 'Cancelada'
                solicitacao.save()                
                return render(request, 'solicitacao_form.html', {
                    'error': 'Nenhum motorista disponível neste horário. A solicitação foi cancelada.',
                    'success': False
                })
    
    return render(request, 'solicitacao_form.html')
