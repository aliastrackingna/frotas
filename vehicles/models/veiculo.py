from django.db import models


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
