import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from vehicles.models import Veiculo, Observacao, Motorista, SolicitacaoMotorista, SolicitacaoViagem, RegistroPortaria
from vehicles.tests.fixtures import criar_motorista, criar_veiculo, criar_solicitacao_viagem, data_futura


class ObservacaoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.veiculo = Veiculo.objects.create(
            placa='OBS1234',
            marca='Honda',
            quantidade_passageiros=2
        )

    def test_adicionar_observacao(self):
        response = self.client.post(
            reverse('observacao_create', args=[self.veiculo.id_veiculo]),
            {'texto': 'Teste de observação'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Observacao.objects.count(), 1)
        self.assertEqual(Observacao.objects.first().texto, 'Teste de observação')

    def test_observacao_vazia_nao_cria(self):
        response = self.client.post(
            reverse('observacao_create', args=[self.veiculo.id_veiculo]),
            {'texto': ''}
        )
        self.assertEqual(Observacao.objects.count(), 0)

    def test_observacao_appear_na_detalhes(self):
        Observacao.objects.create(veiculo=self.veiculo, texto='Observação 1')
        response = self.client.get(reverse('veiculo_detail', args=[self.veiculo.id_veiculo]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Observação 1')

    def test_redirect_para_detalhes_apos_criar(self):
        response = self.client.post(
            reverse('observacao_create', args=[self.veiculo.id_veiculo]),
            {'texto': 'Nova observação'}
        )
        self.assertRedirects(response, reverse('veiculo_detail', args=[self.veiculo.id_veiculo]))


class SolicitacaoMotoristaViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.motorista = Motorista.objects.create(
            nome="Maria Santos",
            tipo_carteira="B"
        )

    def test_listar_solicitacoes(self):
        agora = timezone.now()
        SolicitacaoMotorista.objects.create(
            data_inicio=agora + timedelta(days=1),
            data_fim_prevista=agora + timedelta(days=1, hours=2),
            status='Pendente'
        )
        response = self.client.get(reverse('solicitacao_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pendente')

    def test_detalhes_solicitacao(self):
        agora = timezone.now()
        solicitacao = SolicitacaoMotorista.objects.create(
            data_inicio=agora + timedelta(days=1),
            data_fim_prevista=agora + timedelta(days=1, hours=2),
            status='Confirmada',
            motorista=self.motorista
        )
        response = self.client.get(reverse('solicitacao_detail', args=[solicitacao.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Maria Santos')

    def test_pagina_criar_solicitacao(self):
        response = self.client.get(reverse('solicitacao_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Agendar Solicitação')

    def test_criar_solicitacao_com_motorista_disponivel(self):
        agora = timezone.now()
        data_inicio = (agora + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
        data_fim = (agora + timedelta(days=1, hours=4)).strftime('%Y-%m-%dT%H:%M')
        
        response = self.client.post(reverse('solicitacao_create'), {
            'data_inicio': data_inicio,
            'data_fim_prevista': data_fim,
            'observacao': 'Teste de solicitação'
        })
        
        solicitacao = SolicitacaoMotorista.objects.first()
        self.assertIsNotNone(solicitacao)
        self.assertEqual(solicitacao.status, 'Confirmada')
        self.assertEqual(solicitacao.motorista, self.motorista)

    @pytest.mark.skip(reason="Teste de edge case com race condition")
    def test_criar_solicitacao_sem_motorista_disponivel(self):
        pass

    def test_pagina_gerenciar_solicitacao(self):
        agora = timezone.now()
        solicitacao = SolicitacaoMotorista.objects.create(
            data_inicio=agora + timedelta(days=1),
            data_fim_prevista=agora + timedelta(days=1, hours=2),
            status='Pendente'
        )
        response = self.client.get(reverse('solicitacao_gerenciar', args=[solicitacao.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gerenciar')

    def test_atribuir_motorista(self):
        agora = timezone.now()
        solicitacao = SolicitacaoMotorista.objects.create(
            data_inicio=agora + timedelta(days=1),
            data_fim_prevista=agora + timedelta(days=1, hours=2),
            status='Pendente'
        )
        response = self.client.post(
            reverse('solicitacao_gerenciar', args=[solicitacao.id]),
            {'action': 'atribuir_motorista', 'motorista': self.motorista.id_motorista}
        )
        solicitacao.refresh_from_db()
        self.assertEqual(solicitacao.motorista, self.motorista)
        self.assertEqual(solicitacao.status, 'Confirmada')

    def test_cancelar_solicitacao(self):
        agora = timezone.now()
        solicitacao = SolicitacaoMotorista.objects.create(
            data_inicio=agora + timedelta(days=1),
            data_fim_prevista=agora + timedelta(days=1, hours=2),
            status='Confirmada',
            motorista=self.motorista
        )
        response = self.client.post(
            reverse('solicitacao_gerenciar', args=[solicitacao.id]),
            {'action': 'cancelar'}
        )
        solicitacao.refresh_from_db()
        self.assertEqual(solicitacao.status, 'Cancelada')

    def test_concluir_solicitacao(self):
        agora = timezone.now()
        solicitacao = SolicitacaoMotorista.objects.create(
            data_inicio=agora + timedelta(days=1),
            data_fim_prevista=agora + timedelta(days=1, hours=2),
            status='Confirmada',
            motorista=self.motorista
        )
        response = self.client.post(
            reverse('solicitacao_gerenciar', args=[solicitacao.id]),
            {'action': 'concluir'}
        )
        solicitacao.refresh_from_db()
        self.assertEqual(solicitacao.status, 'Concluida')


class SolicitacaoViagemViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.motorista = Motorista.objects.create(
            nome="Maria Santos",
            tipo_carteira="D"
        )
        self.veiculo = Veiculo.objects.create(
            placa="VIAGEM01",
            marca="Mercedes-Benz",
            quantidade_passageiros=44
        )

    def test_listar_viagens(self):
        agora = timezone.now()
        SolicitacaoViagem.objects.create(
            data_viagem=agora + timedelta(days=1),
            data_fim_prevista=agora + timedelta(days=1, hours=2),
            quantidade_passageiros=30,
            local_embarque="A",
            local_desembarque="B",
            status='Pendente'
        )
        response = self.client.get(reverse('solicitacao_viagem_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pendente')

    def test_detalhes_viagem(self):
        agora = timezone.now()
        viagem = SolicitacaoViagem.objects.create(
            data_viagem=agora + timedelta(days=1),
            data_fim_prevista=agora + timedelta(days=1, hours=2),
            quantidade_passageiros=30,
            local_embarque="Terminal",
            local_desembarque="Aeroporto",
            status='Confirmada',
            veiculo=self.veiculo,
            motorista=self.motorista
        )
        response = self.client.get(reverse('solicitacao_viagem_detail', args=[viagem.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Terminal')

    def test_pagina_criar_viagem(self):
        response = self.client.get(reverse('solicitacao_viagem_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nova Solicitação de Viagem')

    def test_criar_viagem_com_veiculo_e_motorista_disponiveis(self):
        agora = timezone.now()
        data_viagem = (agora + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
        data_fim = (agora + timedelta(days=1, hours=4)).strftime('%Y-%m-%dT%H:%M')
        
        response = self.client.post(reverse('solicitacao_viagem_create'), {
            'data_viagem': data_viagem,
            'data_fim_prevista': data_fim,
            'quantidade_passageiros': '30',
            'local_embarque': 'Escola A',
            'local_desembarque': 'Escola B',
            'itinerario[]': ['Parada 1', 'Parada 2'],
            'observacao': 'Teste de viagem'
        })
        
        viagem = SolicitacaoViagem.objects.first()
        self.assertIsNotNone(viagem)
        self.assertEqual(viagem.status, 'Confirmada')
        self.assertEqual(viagem.veiculo, self.veiculo)
        self.assertEqual(viagem.motorista, self.motorista)

    def test_pagina_gerenciar_viagem(self):
        agora = timezone.now()
        viagem = SolicitacaoViagem.objects.create(
            data_viagem=agora + timedelta(days=1),
            data_fim_prevista=agora + timedelta(days=1, hours=2),
            quantidade_passageiros=30,
            local_embarque="A",
            local_desembarque="B",
            status='Pendente'
        )
        response = self.client.get(reverse('solicitacao_viagem_gerenciar', args=[viagem.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gerenciar')

    def test_atribuir_veiculo_viagem(self):
        agora = timezone.now()
        viagem = SolicitacaoViagem.objects.create(
            data_viagem=agora + timedelta(days=1),
            data_fim_prevista=agora + timedelta(days=1, hours=2),
            quantidade_passageiros=30,
            local_embarque="A",
            local_desembarque="B",
            status='Pendente'
        )
        response = self.client.post(
            reverse('solicitacao_viagem_gerenciar', args=[viagem.id]),
            {'action': 'atribuir_veiculo', 'veiculo': self.veiculo.id_veiculo}
        )
        viagem.refresh_from_db()
        self.assertEqual(viagem.veiculo, self.veiculo)

    def test_atribuir_motorista_viagem(self):
        agora = timezone.now()
        viagem = SolicitacaoViagem.objects.create(
            data_viagem=agora + timedelta(days=1),
            data_fim_prevista=agora + timedelta(days=1, hours=2),
            quantidade_passageiros=30,
            local_embarque="A",
            local_desembarque="B",
            status='Pendente'
        )
        response = self.client.post(
            reverse('solicitacao_viagem_gerenciar', args=[viagem.id]),
            {'action': 'atribuir_motorista', 'motorista': self.motorista.id_motorista}
        )
        viagem.refresh_from_db()
        self.assertEqual(viagem.motorista, self.motorista)

    def test_cancelar_viagem(self):
        agora = timezone.now()
        viagem = SolicitacaoViagem.objects.create(
            data_viagem=agora + timedelta(days=1),
            data_fim_prevista=agora + timedelta(days=1, hours=2),
            quantidade_passageiros=30,
            local_embarque="A",
            local_desembarque="B",
            status='Confirmada',
            veiculo=self.veiculo,
            motorista=self.motorista
        )
        response = self.client.post(
            reverse('solicitacao_viagem_gerenciar', args=[viagem.id]),
            {'action': 'cancelar'}
        )
        viagem.refresh_from_db()
        self.assertEqual(viagem.status, 'Cancelada')

    def test_concluir_viagem(self):
        agora = timezone.now()
        viagem = SolicitacaoViagem.objects.create(
            data_viagem=agora + timedelta(days=1),
            data_fim_prevista=agora + timedelta(days=1, hours=2),
            quantidade_passageiros=30,
            local_embarque="A",
            local_desembarque="B",
            status='Confirmada',
            veiculo=self.veiculo,
            motorista=self.motorista
        )
        response = self.client.post(
            reverse('solicitacao_viagem_gerenciar', args=[viagem.id]),
            {'action': 'concluir'}
        )
        viagem.refresh_from_db()
        self.assertEqual(viagem.status, 'Concluida')


class PortariaViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.motorista = criar_motorista("Motorista Portaria", "D")
        self.veiculo = criar_veiculo("PORT001", "Mercedes-Benz", 44, kms_atual=1000)
        self.viagem = criar_solicitacao_viagem(
            veiculo=self.veiculo,
            motorista=self.motorista,
            status='Confirmada'
        )

    def test_pagina_portaria_lista_viagens_do_dia(self):
        response = self.client.get(reverse('portaria_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Portaria', response.content)

    def test_registrar_saida(self):
        response = self.client.post(
            reverse('portaria_registrar_saida', args=[self.viagem.id]),
            {'km_saida': '1000', 'observacao_saida': 'Teste de saída'}
        )
        self.assertRedirects(response, reverse('portaria_list'))
        
        registro = RegistroPortaria.objects.get(viagem=self.viagem)
        self.assertEqual(registro.km_saida, 1000)
        self.assertIsNotNone(registro.horario_saida)

    def test_registrar_chegada_atualiza_km_veiculo(self):
        RegistroPortaria.objects.create(viagem=self.viagem, km_saida=1000, horario_saida=timezone.now())
        
        response = self.client.post(
            reverse('portaria_registrar_chegada', args=[self.viagem.id]),
            {'km_chegada': '1150', 'observacao_chegada': 'Teste de chegada'}
        )
        self.assertRedirects(response, reverse('portaria_list'))
        
        registro = RegistroPortaria.objects.get(viagem=self.viagem)
        self.assertEqual(registro.km_chegada, 1150)
        
        self.veiculo.refresh_from_db()
        self.assertEqual(self.veiculo.kms_atual, 1150)
