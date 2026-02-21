import pytest
from django.test import TestCase
from vehicles.models import Veiculo, Observacao


class VeiculoModelTest(TestCase):
    def test_criar_veiculo(self):
        veiculo = Veiculo.objects.create(
            placa="ABC1234",
            marca="Toyota",
            quantidade_passageiros=5,
            km_inicial=1000,
            kms_atual=1500
        )
        self.assertEqual(veiculo.placa, "ABC1234")
        self.assertEqual(veiculo.marca, "Toyota")
        self.assertEqual(veiculo.quantidade_passageiros, 5)
        self.assertEqual(veiculo.km_inicial, 1000)
        self.assertEqual(veiculo.kms_atual, 1500)

    def test_str_veiculo(self):
        veiculo = Veiculo.objects.create(
            placa="XYZ5678",
            marca="Honda",
            quantidade_passageiros=2
        )
        self.assertEqual(str(veiculo), "XYZ5678 - Honda")

    def test_placa_unica(self):
        Veiculo.objects.create(
            placa="UNIQUE01",
            marca="Ford",
            quantidade_passageiros=5
        )
        with self.assertRaises(Exception):
            Veiculo.objects.create(
                placa="UNIQUE01",
                marca="Chevrolet",
                quantidade_passageiros=5
            )

    def test_listar_veiculos(self):
        Veiculo.objects.create(placa="AAA1111", marca="VW", quantidade_passageiros=5)
        Veiculo.objects.create(placa="BBB2222", marca="GM", quantidade_passageiros=5)
        veiculos = Veiculo.objects.all()
        self.assertEqual(veiculos.count(), 2)

    def test_atualizar_veiculo(self):
        veiculo = Veiculo.objects.create(
            placa="UPD3333",
            marca="Nissan",
            quantidade_passageiros=5,
            kms_atual=1000
        )
        veiculo.kms_atual = 2000
        veiculo.save()
        veiculo.refresh_from_db()
        self.assertEqual(veiculo.kms_atual, 2000)

    def test_excluir_veiculo(self):
        veiculo = Veiculo.objects.create(
            placa="DEL4444",
            marca="Hyundai",
            quantidade_passageiros=5
        )
        veiculo_id = veiculo.id_veiculo
        veiculo.delete()
        self.assertFalse(Veiculo.objects.filter(id_veiculo=veiculo_id).exists())


class ObservacaoModelTest(TestCase):
    def setUp(self):
        self.veiculo = Veiculo.objects.create(
            placa="OBS5555",
            marca="Kia",
            quantidade_passageiros=5
        )

    def test_criar_observacao(self):
        obs = Observacao.objects.create(
            veiculo=self.veiculo,
            texto="Troca de óleo realizada"
        )
        self.assertEqual(obs.texto, "Troca de óleo realizada")
        self.assertEqual(obs.veiculo.placa, "OBS5555")

    def test_str_observacao(self):
        obs = Observacao.objects.create(
            veiculo=self.veiculo,
            texto="Teste de observação"
        )
        self.assertIn("OBS5555", str(obs))

    def test_veiculo_tem_multiplas_observacoes(self):
        Observacao.objects.create(veiculo=self.veiculo, texto="Observação 1")
        Observacao.objects.create(veiculo=self.veiculo, texto="Observação 2")
        Observacao.objects.create(veiculo=self.veiculo, texto="Observação 3")
        self.assertEqual(self.veiculo.observacoes.count(), 3)

    def test_cascade_exclusao_veiculo(self):
        obs = Observacao.objects.create(
            veiculo=self.veiculo,
            texto="Será excluída"
        )
        obs_id = obs.id
        self.veiculo.delete()
        self.assertFalse(Observacao.objects.filter(id=obs_id).exists())

    def test_listar_observacoes_por_veiculo(self):
        Observacao.objects.create(veiculo=self.veiculo, texto="Primeira")
        Observacao.objects.create(veiculo=self.veiculo, texto="Segunda")
        observacoes = self.veiculo.observacoes.all()
        self.assertEqual(observacoes.count(), 2)

    def test_data_criacao_auto(self):
        obs = Observacao.objects.create(
            veiculo=self.veiculo,
            texto="Com data automática"
        )
        self.assertIsNotNone(obs.data_criacao)
