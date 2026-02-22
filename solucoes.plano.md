# Plano de Implementação - Refatoração Sistema de Gestão de Frotas

## Visão Geral

| Fase | Estimativa | Prioridade |
|------|------------|------------|
| **Fase 1:** Segurança | 6-8h | 🔴 CRÍTICA |
| **Fase 2:** Qualidade | 14-18h | 🟡 ALTA |
| **Fase 3:** Arquitetura | 12-16h | 🟡 MÉDIA |
| **Fase 4:** Produção | 6-8h | 🟢 BAIXA |

**Total:** ~38-50 horas

---

## Fase 1: Segurança (Urgente)

### 1.1 Variáveis de Ambiente (~2h)
- Adicionar `python-decouple` ao `requirements.txt`
- Criar `.env.example` e `.env` local
- Refatorar `settings.py` para usar `config()`

### 1.2 Configurações Críticas (~2h)
- Mover `SECRET_KEY` para variável de ambiente
- Tornar `DEBUG` condicional: `DEBUG = config('DEBUG', default=False, cast=bool)`
- Configurar `ALLOWED_HOSTS` dinamicamente

### 1.3 Autenticação/Autorização (~3h)
- Criar middleware de autenticação global
- Adicionar `@login_required` em todas as ~24 funções de view
- Criar template de login em `templates/registration/login.html`

### 1.4 Segurança HTTP (~1h)
- Adicionar `SECURE_BROWSER_XSS_FILTER`, `SECURE_SSL_REDIRECT`, `X_FRAME_OPTIONS`, etc.
- Wrap com `if not DEBUG:` para ativar apenas em produção

---

## Fase 2: Qualidade de Código

### 2.1 Criar Django Forms (~4h)
Criar `vehicles/forms.py` com:
- `VeiculoForm`, `VeiculoUpdateForm`
- `MotoristaForm`, `MotoristaUpdateForm`
- `SolicitacaoMotoristaForm` (com validação de data)
- `SolicitacaoViagemForm` (com validação de data + itinerario)
- `RegistroPortariaSaidaForm`, `RegistroPortariaChegadaForm`
- `ObservacaoForm`

### 2.2 Extrair Camada de Serviços (~5h)
Criar `vehicles/services.py`:
```python
class AlocacaoService:
    @classmethod
    def criar_solicitacao_motorista(cls, data_inicio, data_fim, observacao)
    @classmethod
    def criar_viagem(cls, data_viagem, data_fim, qtd_passageiros, ...)
    
class PortariaService:
    @staticmethod
    def validar_km_chegada(registro, km_chegada)
    @staticmethod
    def registrar_chegada(viagem, km_chegada, observacao)
```

Atualizar views para usar services (máx 15-20 linhas cada).

### 2.3 Corrigir Typos (~1h)
- `motoristal_*` → `motorista_*` (3 funções)
- `motoresas_*` → `motoristas_*` (2 variáveis)
- Atualizar `urls.py` e `views/__init__.py`

### 2.4 Otimizar Queries ORM (~3h)
- Adicionar `select_related('motorista')` em `solicitacao_list`
- Adicionar `select_related('veiculo', 'solicitacao_motorista')` em `viagem_list`
- Corrigir N+1 em `portaria_list` com `select_related('registro_portaria')`
- Adicionar `prefetch_related('observacoes')` em `veiculo_detail`
- Adicionar `db_index=True` em `status`, `data_inicio`, `data_fim_prevista`

### 2.5 Testes (~2h)
- Executar `pytest`
- Corrigir falhas
- Atualizar cobertura

---

## Fase 3: Arquitetura

### 3.1 Reorganizar Packages (~8h)
Criar estrutura de packages dentro de `vehicles/`:
```
vehicles/
├── veiculos/
│   ├── models.py, forms.py, views.py, urls.py
├── motoristas/
│   ├── models.py, forms.py, views.py, urls.py
├── solicitacoes/
│   ├── models.py, forms.py, services.py, views.py, urls.py
└── portaria/
    ├── models.py, forms.py, services.py, views.py, urls.py
```

### 3.2 Templates (~2h)
- Criar subpastas: `templates/motoristas/`, `templates/solicitacoes/`, `templates/portaria/`
- Mover arquivos para namespaces corretos

### 3.3 Componentização (~2h)
Criar partials em `templates/utils/`:
- `_datetime_picker.html`
- `_date_filter.html`
- `_item_card.html`
- `_actions.html`

---

## Fase 4: Produção

### 4.1 PostgreSQL (~3h)
- Adicionar `psycopg2-binary` ao requirements
- Configurar `DATABASES` condicional (SQLite dev / PostgreSQL prod)
- Executar migrações

### 4.2 Arquivos Estáticos (~1h)
- Adicionar `STATIC_ROOT`, `MEDIA_URL`, `MEDIA_ROOT`
- Baixar Flatpickr localmente
- Extrair JS inline para `static/js/main.js`

### 4.3 Logging (~1h)
- Adicionar configuração de `LOGGING` no `settings.py`
- Opcional: adicionar Sentry

### 4.4 Rate Limiting (~1h, opcional)
- Avaliar necessidade
- Se necessário, adicionar `django-ratelimit`

---

## Ordem de Execução

```
Semana 1: Fase 1 (Segurança)
Semana 2-3: Fase 2 (Qualidade)  
Semana 4: Fase 3 (Arquitetura)
Semana 5: Fase 4 (Produção)
```

---

## Dependências Entre Tarefas

```
Fase 1
├── 1.1 → 1.2 → 1.3 → 1.4
│
Fase 2 (depende de Fase 1)
├── 2.1 → 2.2 → 2.3 → 2.4 → 2.5
│
Fase 3 (depende de Fase 2)
├── 3.1 → 3.2 → 3.3
│
Fase 4 (depende de 1.4)
└── 4.1 → 4.2 → 4.3 → 4.4
```

---

*Plano gerado em 22/02/2026 baseado no diagnóstico arquitetural.*
