from django.db import models
from django.core.exceptions import ValidationError


class Veiculo(models.Model):
    id_veiculo = models.AutoField(primary_key=True)
    placa = models.CharField(max_length=7, unique=True)
    marca = models.CharField(max_length=50)
    quantidade_passageiros = models.PositiveIntegerField()
    km_inicial = models.PositiveIntegerField(default=0)
    kms_atual = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-id_veiculo']

    def __str__(self):
        return f"{self.placa} - {self.marca}"


class Observacao(models.Model):
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE, related_name='observacoes')
    texto = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Observação {self.id} - {self.veiculo.placa}"


class Motorista(models.Model):
    TIPOS_CARTEIRA = [
        ('A', 'A - Motocicleta'),
        ('B', 'B - Carro'),
        ('C', 'C - Caminhão'),
        ('D', 'D - Ônibus'),
        ('E', 'E - Carreta'),
    ]

    id_motorista = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    tipo_carteira = models.CharField(max_length=1, choices=TIPOS_CARTEIRA)

    def clean(self):
        choices = [c[0] for c in self.TIPOS_CARTEIRA]
        if self.tipo_carteira and self.tipo_carteira not in choices:
            raise ValidationError({'tipo_carteira': 'Carteira inválida. Escolha: A, B, C, D ou E'})

    class Meta:
        ordering = ['-id_motorista']

    def __str__(self):
        return f"{self.nome} - Carteira {self.tipo_carteira}"


class SolicitacaoMotorista(models.Model):
    STATUS_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Confirmada', 'Confirmada'),
        ('Concluida', 'Concluída'),
        ('Cancelada', 'Cancelada'),
    ]

    data_inicio = models.DateTimeField()
    data_fim_prevista = models.DateTimeField()
    motorista = models.ForeignKey(Motorista, on_delete=models.SET_NULL, related_name='solicitacoes', null=True, blank=True)
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
    veiculo = models.ForeignKey(Veiculo, on_delete=models.SET_NULL, related_name='solicitacoes_viagem', null=True, blank=True)
    motorista = models.ForeignKey(Motorista, on_delete=models.SET_NULL, related_name='solicitacoes_viagem', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pendente')
    observacao = models.TextField(blank=True, default='')
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Viagem #{self.id} - {self.data_viagem.strftime('%d/%m/%Y')} - {self.get_status_display()}"
