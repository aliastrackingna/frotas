from django.shortcuts import render, get_object_or_404, redirect
from django.db import models, transaction
from django.utils import timezone
from django.http import HttpResponse
from datetime import datetime, timedelta
import random
from .models import Veiculo, Motorista, SolicitacaoMotorista, SolicitacaoViagem, RegistroPortaria


def index(request):
    total_veiculos = Veiculo.objects.count()
    return render(request, 'index.html', {'total_veiculos': total_veiculos})


def veiculo_list(request):
    return render(request, 'vehicles/veiculo_list.html', {'veiculos': Veiculo.objects.all()})


def veiculo_detail(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    return render(request, 'vehicles/veiculo_detail.html', {'veiculo': veiculo})


def veiculo_create(request):
    if request.method == 'POST':
        Veiculo.objects.create(
            placa=request.POST['placa'],
            marca=request.POST['marca'],
            quantidade_passageiros=request.POST['quantidade_passageiros'],
            km_inicial=request.POST.get('km_inicial', 0),
            kms_atual=request.POST.get('kms_atual', 0)
        )
        return redirect('veiculo_list')
    return render(request, 'vehicles/veiculo_form.html')


def veiculo_update(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    if request.method == 'POST':
        veiculo.placa = request.POST['placa']
        veiculo.marca = request.POST['marca']
        veiculo.quantidade_passageiros = request.POST['quantidade_passageiros']
        veiculo.km_inicial = request.POST.get('km_inicial', 0)
        veiculo.kms_atual = request.POST.get('kms_atual', 0)
        veiculo.save()
        return redirect('veiculo_list')
    return render(request, 'vehicles/veiculo_form.html', {'veiculo': veiculo})


def veiculo_delete(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    if request.method == 'POST':
        veiculo.delete()
        return redirect('veiculo_list')
    return render(request, 'vehicles/veiculo_confirm_delete.html', {'veiculo': veiculo})


def observacao_create(request, veiculo_pk):
    veiculo = get_object_or_404(Veiculo, pk=veiculo_pk)
    if request.method == 'POST':
        texto = request.POST.get('texto', '').strip()
        if texto:
            veiculo.observacoes.create(texto=texto)
    return redirect('veiculo_detail', pk=veiculo_pk)


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


def motorista_list(request):
    return render(request, 'motorista_list.html', {'motoristas': Motorista.objects.all()})


def motorista_detail(request, pk):
    motorista = get_object_or_404(Motorista, pk=pk)
    return render(request, 'motorista_detail.html', {'motorista': motorista})


def motorista_create(request):
    if request.method == 'POST':
        Motorista.objects.create(
            nome=request.POST['nome'],
            tipo_carteira=request.POST['tipo_carteira']
        )
        return redirect('motorista_list')
    return render(request, 'motorista_form.html')


def motorista_update(request, pk):
    motorista = get_object_or_404(Motorista, pk=pk)
    if request.method == 'POST':
        motorista.nome = request.POST['nome']
        motorista.tipo_carteira = request.POST['tipo_carteira']
        motorista.save()
        return redirect('motorista_list')
    return render(request, 'motorista_form.html', {'motorista': motorista})


def motorista_delete(request, pk):
    motorista = get_object_or_404(Motorista, pk=pk)
    if request.method == 'POST':
        motorista.delete()
        return redirect('motorista_list')
    return render(request, 'motorista_confirm_delete.html', {'motorista': motorista})


def solicitacao_list(request):
    return render(request, 'solicitacao_list.html', {'solicitacoes': SolicitacaoMotorista.objects.all()})


def solicitacao_detail(request, pk):
    solicitacao = get_object_or_404(SolicitacaoMotorista, pk=pk)
    return render(request, 'solicitacao_detail.html', {'solicitacao': solicitacao})


def solicitacao_gerenciar(request, pk):
    solicitacao = get_object_or_404(SolicitacaoMotorista, pk=pk)
    motoristas_disponiveis = get_motoristas_disponiveis(
        solicitacao.data_inicio, solicitacao.data_fim_prevista
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        veiculo_id = None
        motorista_id = request.POST.get('motorista')
        
        if _processar_action_gerenciar(solicitacao, action, veiculo_id, motorista_id):
            return redirect('solicitacao_detail', pk=pk)
    
    return render(request, 'solicitacao_gerenciar.html', {
        'solicitacao': solicitacao,
        'motoristas': list(motoristas_disponiveis)
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
                return render(request, 'solicitacao_form.html', {
                    'error': 'Nenhum motorista disponível neste horário. A solicitação ficou pendente.',
                    'success': True
                })
    
    return render(request, 'solicitacao_form.html')


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
        motorista_id = request.POST.get('motorista')
        
        if _processar_action_gerenciar(solicitacao, action, veiculo_id, motorista_id):
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
                
                if quantidade_passageiros > capacidade:
                    solicitacao.status = 'Cancelada'
                    solicitacao.observacao = 'Não temos veículos para atender a demanda'
                    solicitacao.save()
                elif (quantidade_passageiros + 3) > capacidade:
                    solicitacao.status = 'Pendente'
                    solicitacao.observacao = 'Veículo disponível com a capacidade maior do que o solicitado, esperando autorização do coordenador'
                    solicitacao.save()
                else:
                    solicitacao.status = 'Confirmada'
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


def portaria_list(request):
    hoje = timezone.now().date()
    amanha = hoje + timedelta(days=1)
    
    viagens = SolicitacaoViagem.objects.filter(
        data_viagem__date__gte=hoje,
        data_viagem__date__lt=amanha
    ).order_by('data_viagem')
    
    viagens_registros = []
    for v in viagens:
        try:
            registro = v.registro_portaria
        except RegistroPortaria.DoesNotExist:
            registro = None
        viagens_registros.append((v, registro))
    
    return render(request, 'portaria_list.html', {
        'viagens_registros': viagens_registros,
        'data_atual': hoje.strftime('%d/%m/%Y')
    })


def portaria_registrar_saida(request, pk):
    viagem = get_object_or_404(SolicitacaoViagem, pk=pk)
    
    if request.method == 'POST':
        km_saida = request.POST.get('km_saida')
        observacao_saida = request.POST.get('observacao_saida', '')
        
        registro, _ = RegistroPortaria.objects.get_or_create(viagem=viagem)
        registro.km_saida = int(km_saida) if km_saida else None
        registro.horario_saida = timezone.now()
        registro.observacao_saida = observacao_saida
        registro.save()
        
        return redirect('portaria_list')
    
    return render(request, 'portaria_registrar.html', {
        'viagem': viagem,
        'acao': 'saida'
    })


def portaria_registrar_chegada(request, pk):
    viagem = get_object_or_404(SolicitacaoViagem, pk=pk)
    
    if request.method == 'POST':
        km_chegada = request.POST.get('km_chegada')
        observacao_chegada = request.POST.get('observacao_chegada', '')
        
        registro = get_object_or_404(RegistroPortaria, viagem=viagem)
        registro.km_chegada = int(km_chegada) if km_chegada else None
        registro.horario_chegada = timezone.now()
        registro.observacao_chegada = observacao_chegada
        registro.save()
        
        if registro.km_chegada and viagem.veiculo:
            viagem.veiculo.kms_atual = registro.km_chegada
            viagem.veiculo.save()
        
        return redirect('portaria_list')
    
    return render(request, 'portaria_registrar.html', {
        'viagem': viagem,
        'acao': 'chegada'
    })
