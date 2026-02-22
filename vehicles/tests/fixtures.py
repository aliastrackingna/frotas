from datetime import timedelta
from django.utils import timezone


def data_futura(dias=1, horas=0):
    """Retorna uma data no futuro"""
    return timezone.now() + timedelta(days=dias, hours=horas)


def formatar_datetime(dt):
    """Formata datetime para string datetime-local"""
    return dt.strftime('%Y-%m-%dT%H:%M')


def criar_motorista(nome="Motorista Teste", tipo_carteira="B"):
    """Cria um motorista para testes"""
    from vehicles.models import Motorista
    return Motorista.objects.create(nome=nome, tipo_carteira=tipo_carteira)


def criar_veiculo(placa="TESTE01", marca="Toyota", passageiros=5, **kwargs):
    """Cria um veículo para testes"""
    from vehicles.models import Veiculo
    data = {
        'placa': placa,
        'marca': marca,
        'quantidade_passageiros': passageiros
    }
    data.update(kwargs)
    return Veiculo.objects.create(**data)


def criar_solicitacao_motorista(data_inicio=None, data_fim=None, **kwargs):
    """Cria uma solicitação de motorista para testes"""
    from vehicles.models import SolicitacaoMotorista
    if data_inicio is None:
        data_inicio = data_futura(dias=1)
    if data_fim is None:
        data_fim = data_futura(dias=1, horas=4)
    return SolicitacaoMotorista.objects.create(
        data_inicio=data_inicio,
        data_fim_prevista=data_fim,
        **kwargs
    )


def criar_solicitacao_viagem(data_viagem=None, data_fim=None, **kwargs):
    """Cria uma solicitação de viagem para testes"""
    from vehicles.models import SolicitacaoViagem
    if data_viagem is None:
        data_viagem = data_futura(dias=1)
    if data_fim is None:
        data_fim = data_futura(dias=1, horas=4)
    
    defaults = {
        'quantidade_passageiros': 10,
        'local_embarque': 'Local A',
        'local_desembarque': 'Local B',
    }
    defaults.update(kwargs)
    
    return SolicitacaoViagem.objects.create(
        data_viagem=data_viagem,
        data_fim_prevista=data_fim,
        **defaults
    )
