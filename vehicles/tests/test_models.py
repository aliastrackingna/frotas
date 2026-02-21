import pytest
from django.test import TestCase
from django.utils import timezone
from vehicles.models import Veiculo, Observacao, Motorista, SolicitacaoMotorista, SolicitacaoViagem, RegistroPortaria
from vehicles.tests.fixtures import (
    data_futura, criar_motorista, criar_veiculo,
    criar_solicitacao_motorista, criar_solicitacao_viagem
)


class VeiculoModelTest(TestCase):
    def test_criar_veiculo(self):
        veiculo = criar_veiculo("ABC1234", "Toyota", 5, km_inicial=1000, kms_atual=1500)
        self.assertEqual(veiculo.placa, "ABC1234")
        self.assertEqual(veiculo.marca, "Toyota")
        self.assertEqual(veiculo.quantidade_passageiros, 5)

    def test_str_veiculo(self):
        veiculo = criar_veiculo("XYZ5678", "Honda", 2)
        self.assertEqual(str(veiculo), "XYZ5678 - Honda")

    def test_placa_unica(self):
        criar_veiculo("UNIQUE01", "Ford", 5)
        with self.assertRaises(Exception):
            criar_veiculo("UNIQUE01", "Chevrolet", 5)

    def test_listar_veiculos(self):
        criar_veiculo("AAA1111", "VW", 5)
        criar_veiculo("BBB2222", "GM", 5)
        self.assertEqual(Veiculo.objects.count(), 2)

    def test_atualizar_veiculo(self):
        veiculo = criar_veiculo("UPD3333", "Nissan", 5, kms_atual=1000)
        veiculo.kms_atual = 2000
        veiculo.save()
        veiculo.refresh_from_db()
        self.assertEqual(veiculo.kms_atual, 2000)

    def test_excluir_veiculo(self):
        veiculo = criar_veiculo("DEL4444", "Hyundai", 5)
        veiculo_id = veiculo.id_veiculo
        veiculo.delete()
        self.assertFalse(Veiculo.objects.filter(id_veiculo=veiculo_id).exists())


class ObservacaoModelTest(TestCase):
    def setUp(self):
        self.veiculo = criar_veiculo("OBS5555", "Kia", 5)

    def test_criar_observacao(self):
        obs = Observacao.objects.create(veiculo=self.veiculo, texto="Troca de óleo")
        self.assertEqual(obs.texto, "Troca de óleo")
        self.assertEqual(obs.veiculo.placa, "OBS5555")

    def test_str_observacao(self):
        obs = Observacao.objects.create(veiculo=self.veiculo, texto="Teste")
        self.assertIn("OBS5555", str(obs))

    def test_veiculo_tem_multiplas_observacoes(self):
        for i in range(3):
            Observacao.objects.create(veiculo=self.veiculo, texto=f"Obs {i}")
        self.assertEqual(self.veiculo.observacoes.count(), 3)

    def test_cascade_exclusao_veiculo(self):
        obs = Observacao.objects.create(veiculo=self.veiculo, texto="Teste")
        obs_id = obs.id
        self.veiculo.delete()
        self.assertFalse(Observacao.objects.filter(id=obs_id).exists())

    def test_listar_observacoes_por_veiculo(self):
        Observacao.objects.create(veiculo=self.veiculo, texto="Primeira")
        Observacao.objects.create(veiculo=self.veiculo, texto="Segunda")
        self.assertEqual(self.veiculo.observacoes.count(), 2)

    def test_data_criacao_auto(self):
        obs = Observacao.objects.create(veiculo=self.veiculo, texto="Teste")
        self.assertIsNotNone(obs.data_criacao)


class SolicitacaoMotoristaModelTest(TestCase):
    def setUp(self):
        self.motorista = criar_motorista("João Silva", "B")

    def test_criar_solicitacao(self):
        solicitacao = criar_solicitacao_motorista(status='Pendente')
        self.assertEqual(solicitacao.status, 'Pendente')

    def test_str_solicitacao(self):
        solicitacao = criar_solicitacao_motorista(status='Pendente')
        self.assertIn('Pendente', str(solicitacao))

    def test_solicitacao_com_motorista(self):
        solicitacao = criar_solicitacao_motorista(
            motorista=self.motorista,
            status='Confirmada'
        )
        self.assertEqual(solicitacao.motorista.nome, "João Silva")
        self.assertEqual(solicitacao.status, 'Confirmada')

    def test_solicitacao_status_default(self):
        solicitacao = criar_solicitacao_motorista()
        self.assertEqual(solicitacao.status, 'Pendente')

    def test_listar_solicitacoes(self):
        criar_solicitacao_motorista(status='Pendente')
        criar_solicitacao_motorista(data_inicio=data_futura(dias=2), status='Confirmada')
        self.assertEqual(SolicitacaoMotorista.objects.count(), 2)

    def test_motorista_tem_solicitacoes(self):
        criar_solicitacao_motorista(motorista=self.motorista, status='Confirmada')
        criar_solicitacao_motorista(
            data_inicio=data_futura(dias=2),
            motorista=self.motorista,
            status='Concluida'
        )
        self.assertEqual(self.motorista.solicitacoes.count(), 2)


class SolicitacaoViagemModelTest(TestCase):
    def setUp(self):
        self.motorista = criar_motorista("João Silva", "D")
        self.veiculo = criar_veiculo("XYZ9999", "Mercedes-Benz", 44)

    def test_criar_viagem(self):
        viagem = criar_solicitacao_viagem(
            quantidade_passageiros=30,
            itinerario=["Parada 1", "Parada 2"],
            status='Pendente'
        )
        self.assertEqual(viagem.status, 'Pendente')
        self.assertEqual(viagem.quantidade_passageiros, 30)
        self.assertEqual(len(viagem.itinerario), 2)

    def test_str_viagem(self):
        viagem = criar_solicitacao_viagem(status='Pendente')
        self.assertIn('Pendente', str(viagem))

    def test_viagem_com_veiculo_e_motorista(self):
        viagem = criar_solicitacao_viagem(
            veiculo=self.veiculo,
            motorista=self.motorista,
            status='Confirmada'
        )
        self.assertEqual(viagem.veiculo.placa, "XYZ9999")
        self.assertEqual(viagem.motorista.nome, "João Silva")

    def test_viagem_status_default(self):
        viagem = criar_solicitacao_viagem()
        self.assertEqual(viagem.status, 'Pendente')

    def test_listar_viagens(self):
        criar_solicitacao_viagem(status='Pendente')
        criar_solicitacao_viagem(data_viagem=data_futura(dias=2), status='Confirmada')
        self.assertEqual(SolicitacaoViagem.objects.count(), 2)

    def test_motorista_tem_viagens(self):
        criar_solicitacao_viagem(motorista=self.motorista, status='Confirmada')
        criar_solicitacao_viagem(
            data_viagem=data_futura(dias=2),
            motorista=self.motorista,
            status='Concluida'
        )
        self.assertEqual(self.motorista.solicitacoes_viagem.count(), 2)

    def test_veiculo_tem_viagens(self):
        criar_solicitacao_viagem(veiculo=self.veiculo, status='Confirmada')
        criar_solicitacao_viagem(
            data_viagem=data_futura(dias=2),
            veiculo=self.veiculo,
            status='Concluida'
        )
        self.assertEqual(self.veiculo.solicitacoes_viagem.count(), 2)


class RegistroPortariaModelTest(TestCase):
    def setUp(self):
        self.motorista = criar_motorista("Motorista Portaria", "D")
        self.veiculo = criar_veiculo("PORT001", "Mercedes-Benz", 44)
        self.viagem = criar_solicitacao_viagem(
            veiculo=self.veiculo,
            motorista=self.motorista,
            status='Confirmada'
        )

    def test_criar_registro_portaria(self):
        registro = RegistroPortaria.objects.create(
            viagem=self.viagem,
            km_saida=1000,
            horario_saida=timezone.now()
        )
        self.assertEqual(registro.km_saida, 1000)
        self.assertEqual(registro.viagem, self.viagem)

    def test_registro_km_chegada_atualiza_veiculo(self):
        pass

    def test_viagem_tem_registro_portaria(self):
        RegistroPortaria.objects.create(viagem=self.viagem, km_saida=500)
        self.assertTrue(hasattr(self.viagem, 'registro_portaria'))
        self.assertEqual(self.viagem.registro_portaria.km_saida, 500)
