from django.db import models
from django.utils import timezone
from datetime import datetime
from ..models import Veiculo, Motorista, SolicitacaoMotorista, SolicitacaoViagem


def _get_ocupados(queryset, data_inicio, data_fim, campo_data, campo_data_fim):
    return queryset.filter(
        status__in=['Confirmada', 'Pendente']
    ).filter(
        models.Q(**{f'{campo_data}__lt': data_fim, f'{campo_data_fim}__gt': data_inicio})
    )


def get_motoristas_disponiveis(data_inicio, data_fim):
    ocupados = _get_ocupados(
        SolicitacaoMotorista.objects, data_inicio, data_fim, 'data_inicio', 'data_fim_prevista'
    ).exclude(motorista__isnull=True).values_list('motorista_id', flat=True)
    return Motorista.objects.exclude(id_motorista__in=ocupados)


def get_motoristas_disponiveis_viagem(data_inicio, data_fim):
    return get_motoristas_disponiveis(data_inicio, data_fim)


def get_veiculos_disponiveis(data_inicio, data_fim, quantidade_passageiros):
    ocupados = _get_ocupados(
        SolicitacaoViagem.objects, data_inicio, data_fim, 'data_viagem', 'data_fim_prevista'
    ).exclude(veiculo__isnull=True).values_list('veiculo_id', flat=True)
    return Veiculo.objects.exclude(id_veiculo__in=ocupados).filter(
        quantidade_passageiros__gte=quantidade_passageiros
    ).order_by('quantidade_passageiros')


def _parse_datetime(date_str):
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        return timezone.make_aware(dt), None
    except (ValueError, TypeError):
        return None, 'Datas inválidas. Use o formato correto.'


def _validar_datas(data_inicio, data_fim):
    if data_inicio < timezone.now():
        return 'A data de início não pode ser no passado.'
    if data_fim <= data_inicio:
        return 'A data de retorno deve ser posterior à data de início.'
    return None


def _atualizar_status_solicitacao(solicitacao):
    if isinstance(solicitacao, SolicitacaoViagem):
        if solicitacao.motorista and solicitacao.veiculo:
            solicitacao.status = 'Confirmada'
            solicitacao.save()
    elif isinstance(solicitacao, SolicitacaoMotorista):
        if solicitacao.motorista:
            solicitacao.status = 'Confirmada'
            solicitacao.save()


def _processar_action_gerenciar(solicitacao, action, veiculo_id=None, motorista_id=None):
    actions = {
        'cancelar': lambda s: setattr(s, 'status', 'Cancelada'),
        'confirmar': lambda s: setattr(s, 'status', 'Confirmada'),
        'concluir': lambda s: setattr(s, 'status', 'Concluida'),
    }
    
    if action == 'atribuir_motorista' and motorista_id:
        solicitacao.motorista_id = motorista_id
        _atualizar_status_solicitacao(solicitacao)
    elif action == 'atribuir_veiculo' and veiculo_id:
        solicitacao.veiculo_id = veiculo_id
        _atualizar_status_solicitacao(solicitacao)
    elif action in actions:
        actions[action](solicitacao)
    else:
        return False
    
    solicitacao.save()
    return True
