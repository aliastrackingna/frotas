from django.db import models
from vehicles.models.veiculo import Veiculo
from vehicles.models.motorista import Motorista


class SolicitacaoMotorista(models.Model):
    STATUS_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Confirmada', 'Confirmada'),
        ('Concluida', 'Concluída'),
        ('Cancelada', 'Cancelada'),
    ]

    data_inicio = models.DateTimeField()
    data_fim_prevista = models.DateTimeField()
    motorista = models.ForeignKey(
        Motorista,
        on_delete=models.SET_NULL,
        related_name='solicitacoes',
        null=True,
        blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pendente')
    observacao = models.TextField(blank=True, default='')
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Solicitação #{self.id} - {self.data_inicio.strftime('%d/%m/%Y')} - {self.get_status_display()}"


class SolicitacaoViagem(models.Model):
    STATUS_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Confirmada', 'Confirmada'),
        ('Concluida', 'Concluída'),
        ('Cancelada', 'Cancelada'),
    ]

    data_viagem = models.DateTimeField()
    data_fim_prevista = models.DateTimeField()
    quantidade_passageiros = models.PositiveIntegerField()
    local_embarque = models.CharField(max_length=200)
    local_desembarque = models.CharField(max_length=200)
    itinerario = models.JSONField(default=list)
    veiculo = models.ForeignKey(
        Veiculo,
        on_delete=models.SET_NULL,
        related_name='solicitacoes_viagem',
        null=True,
        blank=True
    )
    solicitacao_motorista = models.ForeignKey(
        SolicitacaoMotorista,
        on_delete=models.SET_NULL,
        related_name='viagem',
        null=True,
        blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pendente')
    observacao = models.TextField(blank=True, default='')
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Viagem #{self.id} - {self.data_viagem.strftime('%d/%m/%Y')} - {self.get_status_display()}"


class RegistroPortaria(models.Model):
    viagem = models.OneToOneField(
        SolicitacaoViagem,
        on_delete=models.CASCADE,
        related_name='registro_portaria'
    )
    km_saida = models.PositiveIntegerField(null=True, blank=True)
    km_chegada = models.PositiveIntegerField(null=True, blank=True)
    horario_saida = models.DateTimeField(null=True, blank=True)
    horario_chegada = models.DateTimeField(null=True, blank=True)
    observacao_saida = models.TextField(blank=True, default='')
    observacao_chegada = models.TextField(blank=True, default='')
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Registro Portaria - Viagem #{self.viagem_id}"
