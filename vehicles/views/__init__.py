from .veiculo_views import (
    index, veiculo_list, veiculo_detail, veiculo_create,
    veiculo_update, veiculo_delete, observacao_create
)
from .motorista_views import (
    motorista_list, motorista_detail,
    motoristal_create,
    motoristal_update, motoristal_delete
)
from .solicitacao_views import (
    solicitacao_list, solicitacao_detail, solicitacao_create,
    solicitacao_gerenciar
)
from .viagem_views import (
    solicitacao_viagem_list, solicitacao_viagem_detail,
    solicitacao_viagem_create, solicitacao_viagem_gerenciar
)
from .portaria_views import (
    portaria_list, portaria_registrar_saida, portaria_registrar_chegada
)
