from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from datetime import timedelta
from ..models import SolicitacaoViagem, RegistroPortaria


def portaria_list(request):
    hoje = timezone.now().date()
    amanha = hoje + timedelta(days=1)
    
    todas_viagens = SolicitacaoViagem.objects.filter(
        data_viagem__date__gte=hoje,
        data_viagem__date__lt=amanha
    ).exclude(
        status='Cancelada'
    ).order_by('data_viagem')
    
    concluidas = []
    pendentes = []
    
    for v in todas_viagens:
        try:
            registro = v.registro_portaria
        except RegistroPortaria.DoesNotExist:
            registro = None
        
        if registro and registro.horario_chegada:
            concluidas.append((v, registro))
        else:
            pendentes.append((v, registro))
    
    pendentes_outras_datas = SolicitacaoViagem.objects.filter(
        data_viagem__date__lt=hoje
    ).exclude(
        registro_portaria__horario_chegada__isnull=False
    ).order_by('-data_viagem')[:10]
    
    for v in pendentes_outras_datas:
        try:
            registro = v.registro_portaria
        except RegistroPortaria.DoesNotExist:
            registro = None
        pendentes.append((v, registro))
    
    stats = {
        'total': len(concluidas) + len(pendentes),
        'saidas': len([p for p in pendentes if p[1] and p[1].horario_saida]) + len([c for c in concluidas if c[1] and c[1].horario_saida]),
        'chegadas': len(concluidas),
        'pendentes': len(pendentes)
    }
    
    return render(request, 'portaria_list.html', {
        'concluidas': concluidas,
        'pendentes': pendentes,
        'stats': stats,
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
    registro = get_object_or_404(RegistroPortaria, viagem=viagem)
    erro = None
    
    if request.method == 'POST':
        km_chegada = request.POST.get('km_chegada')
        observacao_chegada = request.POST.get('observacao_chegada', '')
        
        if km_chegada:
            km_chegada = int(km_chegada)
            if registro.km_saida and km_chegada < registro.km_saida:
                erro = f'KM de chegada ({km_chegada}) não pode ser menor que KM de saída ({registro.km_saida})'
            else:
                registro.km_chegada = km_chegada
                registro.horario_chegada = timezone.now()
                registro.observacao_chegada = observacao_chegada
                registro.save()
                
                if registro.km_chegada and viagem.veiculo:
                    viagem.veiculo.kms_atual = registro.km_chegada
                    viagem.veiculo.save()
                
                return redirect('portaria_list')
        else:
            erro = 'KM de chegada é obrigatório'
    
    return render(request, 'portaria_registrar.html', {
        'viagem': viagem,
        'acao': 'chegada',
        'registro': registro,
        'erro': erro
    })
