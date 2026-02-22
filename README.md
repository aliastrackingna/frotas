# Frotas - Sistema de Gestão de Frotas

Sistema Django para gestão de veículos, motoristas e viagens.

## Funcionalidades

- **Veículos**: Cadastro, listagem, edição e exclusão de veículos com placa única, marca, capacidade de passageiros e controle de KM
- **Motoristas**: Cadastro de motoristas com tipo de carteira (A, B, C, D, E)
- **Solicitações de Motorista**: Agendamento de horários para motoristas
- **Solicitações de Viagem**: Agendamento de viagens com veículo, motorista, itinerário e capacidade de passageiros
- **Portaria**: Registro de saída e chegada de viagens com controle de KM e horário

## Tech Stack

- Django 6.0
- Python 3.14
- Bootstrap 5 (templates)
- Pytest + pytest-cov (testes)

## Setup

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Criar banco de dados
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Executar servidor
python manage.py runserver
```

## Testes

```bash
# Executar todos os testes
pytest -v

# Executar com coverage
pytest --cov=vehicles --cov-report=html
```

**Cobertura de testes: 97%**

## URLs

| Rota | Descrição |
|------|-----------|
| `/` | Dashboard |
| `/motoristas/` | Listar motoristas |
| `/motoristas/novo/` | Cadastrar motorista |
| `/solicitacoes/` | Listar solicitações de motorista |
| `/solicitacoes/nova/` | Criar solicitação de motorista |
| `/solicitacoes/viagem/` | Listar viagens |
| `/solicitacoes/viagem/nova/` | Criar viagem |
| `/portaria/` | Lista de portaria (viagens do dia) |
| `/list/` | Listar veículos |
| `/novo/` | Cadastrar veículo |

## Modelos

- **Veiculo**: placa, marca, quantidade_passageiros, km_inicial, kms_atual
- **Observacao**: relacionada a veículo
- **Motorista**: nome, tipo_carteira (A-E)
- **SolicitacaoMotorista**: data_inicio, data_fim_prevista, motorista, status
- **SolicitacaoViagem**: data_viagem, quantidade_passageiros, local_embarque, local_desembarque, itinerario, veiculo, motorista, status
- **RegistroPortaria**: km_saida, km_chegada, horario_saida, horario_chegada (relacionado à viagem)
