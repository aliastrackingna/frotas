from rest_framework import viewsets
from .models import Veiculo, Observacao
from .serializers import VeiculoSerializer, ObservacaoSerializer


class VeiculoViewSet(viewsets.ModelViewSet):
    queryset = Veiculo.objects.all()
    serializer_class = VeiculoSerializer


class ObservacaoViewSet(viewsets.ModelViewSet):
    queryset = Observacao.objects.all()
    serializer_class = ObservacaoSerializer
