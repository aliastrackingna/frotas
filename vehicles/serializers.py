from rest_framework import serializers
from .models import Veiculo, Observacao


class ObservacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observacao
        fields = ['id', 'veiculo', 'texto', 'data_criacao']
        read_only_fields = ['data_criacao']


class VeiculoSerializer(serializers.ModelSerializer):
    observacoes = ObservacaoSerializer(many=True, read_only=True)

    class Meta:
        model = Veiculo
        fields = ['id_veiculo', 'placa', 'marca', 'quantidade_passageiros',
                  'km_inicial', 'kms_atual', 'observacoes']
        read_only_fields = ['id_veiculo']
