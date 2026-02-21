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
