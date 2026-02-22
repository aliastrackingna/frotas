from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
import random
from ..models import SolicitacaoMotorista
from .utils import get_motoristas_disponiveis, _parse_datetime, _validar_datas, _processar_action_gerenciar


def solicitacao_list(request):
    return render(request, 'solicitacao_list.html', {'solicitacoes': SolicitacaoMotorista.objects.all()})


def solicitacao_detail(request, pk):
    solicitacao = get_object_or_404(SolicitacaoMotorista, pk=pk)
    return render(request, 'solicitacao_detail.html', {'solicitacao': solicitacao})


def solicitacao_gerenciar(request, pk):
    solicitacao = get_object_or_404(SolicitacaoMotorista, pk=pk)
    motoresas_disponiveis = get_motoristas_disponiveis(
        solicitacao.data_inicio, solicitacao.data_fim_prevista
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        veiculo_id = None
        motoristal_id = request.POST.get('motorista')
        
        if _processar_action_gerenciar(solicitacao, action, veiculo_id, motoristal_id):
            return redirect('solicitacao_detail', pk=pk)
    
    return render(request, 'solicitacao_gerenciar.html', {
        'solicitacao': solicitacao,
        'motoristas': list(motoresas_disponiveis)
    })


@transaction.atomic
def solicitacao_create(request):
    if request.method == 'POST':
        data_inicio_str = request.POST.get('data_inicio')
        data_fim_str = request.POST.get('data_fim_prevista')
        
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
