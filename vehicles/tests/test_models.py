import pytest
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from vehicles.models import Veiculo, Observacao, Motorista, SolicitacaoMotorista, SolicitacaoViagem


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


class SolicitacaoMotoristaModelTest(TestCase):
    def setUp(self):
        self.motorista = Motorista.objects.create(
            nome="João Silva",
            tipo_carteira="B"
        )

    def test_criar_solicitacao(self):
        agora = timezone.now()
        inicio = agora + timedelta(days=1)
        fim = agora + timedelta(days=1, hours=4)
        
        solicitacao = SolicitacaoMotorista.objects.create(
            data_inicio=inicio,
            data_fim_prevista=fim,
            status='Pendente'
        )
        self.assertEqual(solicitacao.status, 'Pendente')

    def test_str_solicitacao(self):
        agora = timezone.now()
        inicio = agora + timedelta(days=1)
        fim = agora + timedelta(days=1, hours=4)
        
        solicitacao = SolicitacaoMotorista.objects.create(
            data_inicio=inicio,
            data_fim_prevista=fim,
            status='Pendente'
        )
        self.assertIn('Pendente', str(solicitacao))

    def test_solicitacao_com_motorista(self):
        agora = timezone.now()
        inicio = agora + timedelta(days=1)
        fim = agora + timedelta(days=1, hours=4)
        
        solicitacao = SolicitacaoMotorista.objects.create(
            data_inicio=inicio,
            data_fim_prevista=fim,
            motorista=self.motorista,
            status='Confirmada'
        )
        self.assertEqual(solicitacao.motorista.nome, "João Silva")
        self.assertEqual(solicitacao.status, 'Confirmada')

    def test_solicitacao_status_default(self):
        agora = timezone.now()
        inicio = agora + timedelta(days=1)
        fim = agora + timedelta(days=1, hours=4)
        
        solicitacao = SolicitacaoMotorista.objects.create(
            data_inicio=inicio,
            data_fim_prevista=fim
        )
        self.assertEqual(solicitacao.status, 'Pendente')

    def test_listar_solicitacoes(self):
        agora = timezone.now()
        
        SolicitacaoMotorista.objects.create(
            data_inicio=agora + timedelta(days=1),
            data_fim_prevista=agora + timedelta(days=1, hours=2),
            status='Pendente'
        )
        SolicitacaoMotorista.objects.create(
            data_inicio=agora + timedelta(days=2),
            data_fim_prevista=agora + timedelta(days=2, hours=2),
            status='Confirmada'
        )
        solicitacoes = SolicitacaoMotorista.objects.all()
        self.assertEqual(solicitacoes.count(), 2)

    def test_motorista_tem_solicitacoes(self):
        agora = timezone.now()
        
        SolicitacaoMotorista.objects.create(
            data_inicio=agora + timedelta(days=1),
            data_fim_prevista=agora + timedelta(days=1, hours=4),
            motorista=self.motorista,
            status='Confirmada'
        )
        SolicitacaoMotorista.objects.create(
            data_inicio=agora + timedelta(days=2),
            data_fim_prevista=agora + timedelta(days=2, hours=4),
            motorista=self.motorista,
            status='Concluida'
        )
        self.assertEqual(self.motorista.solicitacoes.count(), 2)


class SolicitacaoViagemModelTest(TestCase):
    def setUp(self):
        self.motorista = Motorista.objects.create(
            nome="João Silva",
            tipo_carteira="D"
        )
        self.veiculo = Veiculo.objects.create(
            placa="XYZ9999",
            marca="Mercedes-Benz",
            quantidade_passageiros=44
        )

    def test_criar_viagem(self):
        agora = timezone.now()
        viagem = SolicitacaoViagem.objects.create(
            data_viagem=agora + timedelta(days=1),
            data_fim_prevista=agora + timedelta(days=1, hours=8),
            quantidade_passageiros=30,
            local_embarque="Terminal Central",
            local_desembarque="Aeroporto Internacional",
            itinerario=["Parada 1", "Parada 2"],
            status='Pendente'
        )
        self.assertEqual(viagem.status, 'Pendente')
        self.assertEqual(viagem.quantidade_passageiros, 30)
        self.assertEqual(len(viagem.itinerario), 2)

    def test_str_viagem(self):
        agora = timezone.now()
        viagem = SolicitacaoViagem.objects.create(
            data_viagem=agora + timedelta(days=1),
            data_fim_prevista=agora + timedelta(days=1, hours=4),
            quantidade_passageiros=20,
            local_embarque="Hospital",
            local_desembarque="Centro",
            status='Pendente'
        )
        self.assertIn('Pendente', str(viagem))

    def test_viagem_com_veiculo_e_motorista(self):
        agora = timezone.now()
        viagem = SolicitacaoViagem.objects.create(
            data_viagem=agora + timedelta(days=1),
            data_fim_prevista=agora + timedelta(days=1, hours=4),
            quantidade_passageiros=40,
            local_embarque="Escola A",
            local_desembarque="Escola B",
            veiculo=self.veiculo,
            motorista=self.motorista,
            status='Confirmada'
        )
        self.assertEqual(viagem.veiculo.placa, "XYZ9999")
        self.assertEqual(viagem.motorista.nome, "João Silva")
        self.assertEqual(viagem.status, 'Confirmada')

    def test_viagem_status_default(self):
        agora = timezone.now()
        viagem = SolicitacaoViagem.objects.create(
            data_viagem=agora + timedelta(days=1),
            data_fim_prevista=agora + timedelta(days=1, hours=4),
            quantidade_passageiros=10,
            local_embarque="A",
            local_desembarque="B"
        )
        self.assertEqual(viagem.status, 'Pendente')

    def test_listar_viagens(self):
        agora = timezone.now()
        
        SolicitacaoViagem.objects.create(
            data_viagem=agora + timedelta(days=1),
            data_fim_prevista=agora + timedelta(days=1, hours=2),
            quantidade_passageiros=10,
            local_embarque="A",
            local_desembarque="B",
            status='Pendente'
        )
        SolicitacaoViagem.objects.create(
            data_viagem=agora + timedelta(days=2),
            data_fim_prevista=agora + timedelta(days=2, hours=2),
            quantidade_passageiros=20,
            local_embarque="C",
            local_desembarque="D",
            status='Confirmada'
        )
        viagens = SolicitacaoViagem.objects.all()
        self.assertEqual(viagens.count(), 2)

    def test_motorista_tem_viagens(self):
        agora = timezone.now()
        
        SolicitacaoViagem.objects.create(
            data_viagem=agora + timedelta(days=1),
            data_fim_prevista=agora + timedelta(days=1, hours=4),
            quantidade_passageiros=30,
            local_embarque="X",
            local_desembarque="Y",
            motorista=self.motorista,
            status='Confirmada'
        )
        SolicitacaoViagem.objects.create(
            data_viagem=agora + timedelta(days=2),
            data_fim_prevista=agora + timedelta(days=2, hours=4),
            quantidade_passageiros=25,
            local_embarque="W",
            local_desembarque="Z",
            motorista=self.motorista,
            status='Concluida'
        )
        self.assertEqual(self.motorista.solicitacoes_viagem.count(), 2)

    def test_veiculo_tem_viagens(self):
        agora = timezone.now()
        
        SolicitacaoViagem.objects.create(
            data_viagem=agora + timedelta(days=1),
            data_fim_prevista=agora + timedelta(days=1, hours=4),
            quantidade_passageiros=40,
            local_embarque="A",
            local_desembarque="B",
            veiculo=self.veiculo,
            status='Confirmada'
        )
        SolicitacaoViagem.objects.create(
            data_viagem=agora + timedelta(days=2),
            data_fim_prevista=agora + timedelta(days=2, hours=4),
            quantidade_passageiros=35,
            local_embarque="C",
            local_desembarque="D",
            veiculo=self.veiculo,
            status='Concluida'
        )
        self.assertEqual(self.veiculo.solicitacoes_viagem.count(), 2)
