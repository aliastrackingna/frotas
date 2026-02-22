from vehicles.services import (
    get_motoristas_disponiveis,
    get_veiculos_disponiveis,
    _parse_datetime,
    _validar_datas,
    processar_action_gerenciar as _processar_action_gerenciar_service,
)


def _processar_action_gerenciar(solicitacao, action, **kwargs):
    return _processar_action_gerenciar_service(solicitacao, action, **kwargs)
