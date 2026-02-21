from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from datetime import timedelta
from ..models import SolicitacaoViagem, RegistroPortaria


def portaria_list(request):
    hoje = timezone.now().date()
    amanha = hoje + timedelta(days=1)
    
    viagens = SolicitacaoViagem.objects.filter(
        data_viagem__date__gte=hoje,
        data_viagem__date__lt=amanha
    ).order_by('data_viagem')
    
    viagens_registros = []
    pendentes = []
    for v in viagens:
        try:
            registro = v.registro_portaria
        except RegistroPortaria.DoesNotExist:
            registro = None
        
        if registro and registro.horario_chegada:
            viagens_registros.append((v, registro))
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
    
    viagens_registros.extend(pendentes)
    
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
