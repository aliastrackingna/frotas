import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from vehicles.models import Veiculo, Observacao


class VeiculoAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.veiculo_data = {
            'placa': 'ABC1234',
            'marca': 'Toyota',
            'quantidade_passageiros': 5,
            'km_inicial': 1000,
            'kms_atual': 1500
        }

    def test_listar_veiculos(self):
        Veiculo.objects.create(**self.veiculo_data)
        response = self.client.get('/api/veiculos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_criar_veiculo(self):
        response = self.client.post('/api/veiculos/', self.veiculo_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Veiculo.objects.count(), 1)
        self.assertEqual(Veiculo.objects.first().placa, 'ABC1234')

    def test_detalhes_veiculo(self):
        veiculo = Veiculo.objects.create(**self.veiculo_data)
        response = self.client.get(f'/api/veiculos/{veiculo.id_veiculo}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['placa'], 'ABC1234')

    def test_atualizar_veiculo(self):
        veiculo = Veiculo.objects.create(**self.veiculo_data)
        response = self.client.patch(
            f'/api/veiculos/{veiculo.id_veiculo}/',
            {'kms_atual': 2000},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        veiculo.refresh_from_db()
        self.assertEqual(veiculo.kms_atual, 2000)

    def test_excluir_veiculo(self):
        veiculo = Veiculo.objects.create(**self.veiculo_data)
        response = self.client.delete(f'/api/veiculos/{veiculo.id_veiculo}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Veiculo.objects.count(), 0)


class ObservacaoAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.veiculo = Veiculo.objects.create(
            placa='OBS1234',
            marca='Honda',
            quantidade_passageiros=2
        )
        self.observacao_data = {
            'veiculo': self.veiculo.id_veiculo,
            'texto': 'Teste de observação'
        }

    def test_criar_observacao(self):
        response = self.client.post('/api/observacoes/', self.observacao_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Observacao.objects.count(), 1)

    def test_listar_observacoes(self):
        Observacao.objects.create(veiculo=self.veiculo, texto='Obs 1')
        Observacao.objects.create(veiculo=self.veiculo, texto='Obs 2')
        response = self.client.get('/api/observacoes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_observacoes_relacionadas_veiculo(self):
        Observacao.objects.create(veiculo=self.veiculo, texto='Primeira')
        Observacao.objects.create(veiculo=self.veiculo, texto='Segunda')
        response = self.client.get(f'/api/veiculos/{self.veiculo.id_veiculo}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['observacoes']), 2)

    def test_excluir_observacao(self):
        obs = Observacao.objects.create(veiculo=self.veiculo, texto='Para excluir')
        response = self.client.delete(f'/api/observacoes/{obs.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Observacao.objects.count(), 0)
