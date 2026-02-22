from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from vehicles.models import Veiculo, Motorista, SolicitacaoMotorista, SolicitacaoViagem


class SolicitacaoViagemViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
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
        solicitacao_motorista = SolicitacaoMotorista.objects.create(
            data_inicio=agora + timedelta(days=1),
            data_fim_prevista=agora + timedelta(days=1, hours=2),
            motorista=self.motorista,
            status='Confirmada'
        )
        viagem = SolicitacaoViagem.objects.create(
            data_viagem=agora + timedelta(days=1),
            data_fim_prevista=agora + timedelta(days=1, hours=2),
            quantidade_passageiros=30,
            local_embarque="Terminal",
            local_desembarque="Aeroporto",
            status='Confirmada',
            veiculo=self.veiculo,
            solicitacao_motorista=solicitacao_motorista
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
        data_viagem = (agora + timedelta(days=100))
        data_fim = (agora + timedelta(days=100, hours=4))
        
        response = self.client.post(reverse('solicitacao_viagem_create'), {
            'data_viagem_data': data_viagem.strftime('%Y-%m-%d'),
            'data_viagem_hora': data_viagem.strftime('%H:%M'),
            'data_fim_prevista_data': data_fim.strftime('%Y-%m-%d'),
            'data_fim_prevista_hora': data_fim.strftime('%H:%M'),
            'quantidade_passageiros': '15',
            'local_embarque': 'Escola A',
            'local_desembarque': 'Escola B',
        })
        
        viagem = SolicitacaoViagem.objects.last()
        self.assertIsNotNone(viagem)
        self.assertIn(viagem.status, ['Confirmada', 'Pendente'])

    def test_criar_viagem_capacidade_proxima_pendente(self):
        agora = timezone.now()
        data_viagem = (agora + timedelta(days=100))
        data_fim = (agora + timedelta(days=100, hours=4))
        
        response = self.client.post(reverse('solicitacao_viagem_create'), {
            'data_viagem_data': data_viagem.strftime('%Y-%m-%d'),
            'data_viagem_hora': data_viagem.strftime('%H:%M'),
            'data_fim_prevista_data': data_fim.strftime('%Y-%m-%d'),
            'data_fim_prevista_hora': data_fim.strftime('%H:%M'),
            'quantidade_passageiros': '25',
            'local_embarque': 'A',
            'local_desembarque': 'B',
        })
        
        viagem = SolicitacaoViagem.objects.last()
        self.assertIn(viagem.status, ['Confirmada', 'Pendente'])

    def test_criar_viagem_itinerario(self):
        agora = timezone.now()
        data_viagem = (agora + timedelta(days=100))
        data_fim = (agora + timedelta(days=100, hours=4))
        
        response = self.client.post(reverse('solicitacao_viagem_create'), {
            'data_viagem_data': data_viagem.strftime('%Y-%m-%d'),
            'data_viagem_hora': data_viagem.strftime('%H:%M'),
            'data_fim_prevista_data': data_fim.strftime('%Y-%m-%d'),
            'data_fim_prevista_hora': data_fim.strftime('%H:%M'),
            'quantidade_passageiros': '20',
            'local_embarque': 'Escola Central',
            'local_desembarque': 'Centro',
            'itinerario[]': ['Parada A', 'Parada B', 'Parada C'],
            'observacao': 'Viagem de campo'
        })
        
        viagem = SolicitacaoViagem.objects.last()
        self.assertEqual(viagem.itinerario, ['Parada A', 'Parada B', 'Parada C'])
        self.assertEqual(viagem.status, 'Pendente')

    def test_criar_viagem_formato_data_invalido(self):
        response = self.client.post(reverse('solicitacao_viagem_create'), {
            'data_viagem_data': 'data-invalida',
            'data_viagem_hora': '10:00',
            'data_fim_prevista_data': 'outra-data-invalida',
            'data_fim_prevista_hora': '14:00',
            'quantidade_passageiros': '30',
            'local_embarque': 'A',
            'local_desembarque': 'B',
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Datas inválidas')

    def test_criar_viagem_data_obrigatoria(self):
        response = self.client.post(reverse('solicitacao_viagem_create'), {
            'data_viagem_data': '',
            'data_viagem_hora': '10:00',
            'data_fim_prevista_data': '2026-12-31',
            'data_fim_prevista_hora': '14:00',
            'quantidade_passageiros': '15',
            'local_embarque': 'A',
            'local_desembarque': 'B',
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'obrigatórios')

    def test_criar_viagem_hora_obrigatoria(self):
        response = self.client.post(reverse('solicitacao_viagem_create'), {
            'data_viagem_data': '2026-12-31',
            'data_viagem_hora': '',
            'data_fim_prevista_data': '2026-12-31',
            'data_fim_prevista_hora': '14:00',
            'quantidade_passageiros': '15',
            'local_embarque': 'A',
            'local_desembarque': 'B',
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'obrigatórios')

    def test_listar_viagens_com_filtro_data_inicio(self):
        agora = timezone.now()
        SolicitacaoViagem.objects.create(
            data_viagem=agora + timedelta(days=5),
            data_fim_prevista=agora + timedelta(days=5, hours=4),
            quantidade_passageiros=20,
            local_embarque='A',
            local_desembarque='B',
            status='Confirmada'
        )
        
        data_filtro = (agora + timedelta(days=5)).strftime('%Y-%m-%d')
        response = self.client.get(f'{reverse("solicitacao_viagem_list")}?data_inicio={data_filtro}')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A')

    def test_listar_viagens_com_filtro_data_fim(self):
        agora = timezone.now()
        SolicitacaoViagem.objects.create(
            data_viagem=agora + timedelta(days=10),
            data_fim_prevista=agora + timedelta(days=10, hours=4),
            quantidade_passageiros=20,
            local_embarque='X',
            local_desembarque='Y',
            status='Confirmada'
        )
        
        data_filtro = (agora + timedelta(days=10)).strftime('%Y-%m-%d')
        response = self.client.get(f'{reverse("solicitacao_viagem_list")}?data_fim={data_filtro}')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'X')

    def test_listar_viagens_sem_filtro(self):
        agora = timezone.now()
        SolicitacaoViagem.objects.create(
            data_viagem=agora + timedelta(days=7),
            data_fim_prevista=agora + timedelta(days=7, hours=4),
            quantidade_passageiros=10,
            local_embarque='Teste',
            local_desembarque='Teste2',
            status='Pendente'
        )
        
        response = self.client.get(reverse('solicitacao_viagem_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Teste')

    def test_listar_viagens_com_filtro_data_inicio_e_fim(self):
        agora = timezone.now()
        SolicitacaoViagem.objects.create(
            data_viagem=agora + timedelta(days=8),
            data_fim_prevista=agora + timedelta(days=8, hours=4),
            quantidade_passageiros=15,
            local_embarque='Filtrado',
            local_desembarque='Filtrado2',
            status='Confirmada'
        )
        
        data_inicio = (agora + timedelta(days=7)).strftime('%Y-%m-%d')
        data_fim = (agora + timedelta(days=9)).strftime('%Y-%m-%d')
        response = self.client.get(f'{reverse("solicitacao_viagem_list")}?data_inicio={data_inicio}&data_fim={data_fim}')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Filtrado')

    def test_criar_viagem_validacao_data_retorno_menor(self):
        agora = timezone.now()
        data_viagem = (agora + timedelta(days=10))
        data_fim = (agora + timedelta(days=10, hours=-2))  # menor que início
        
        response = self.client.post(reverse('solicitacao_viagem_create'), {
            'data_viagem_data': data_viagem.strftime('%Y-%m-%d'),
            'data_viagem_hora': data_viagem.strftime('%H:%M'),
            'data_fim_prevista_data': data_fim.strftime('%Y-%m-%d'),
            'data_fim_prevista_hora': data_fim.strftime('%H:%M'),
            'quantidade_passageiros': '15',
            'local_embarque': 'A',
            'local_desembarque': 'B',
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'posterior')


class ViagemGerenciarViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.motorista = Motorista.objects.create(
            nome="Motorista Viagem",
            tipo_carteira="D"
        )
        self.veiculo = Veiculo.objects.create(
            placa="VGTEST02",
            marca="Volvo",
            quantidade_passageiros=44
        )
        self.solicitacao_motorista = SolicitacaoMotorista.objects.create(
            data_inicio=timezone.now() + timedelta(days=5),
            data_fim_prevista=timezone.now() + timedelta(days=5, hours=4),
            motorista=self.motorista,
            status='Confirmada'
        )
        self.viagem = SolicitacaoViagem.objects.create(
            data_viagem=timezone.now() + timedelta(days=5),
            data_fim_prevista=timezone.now() + timedelta(days=5, hours=4),
            quantidade_passageiros=30,
            local_embarque="Terminal A",
            local_desembarque="Terminal B",
            status='Pendente'
        )
        self.veiculo = Veiculo.objects.create(
            placa="VGTEST01",
            marca="Volvo",
            quantidade_passageiros=44
        )
        self.solicitacao_motorista = SolicitacaoMotorista.objects.create(
            data_inicio=timezone.now() + timedelta(days=5),
            data_fim_prevista=timezone.now() + timedelta(days=5, hours=4),
            motorista=self.motorista,
            status='Confirmada'
        )
        self.viagem = SolicitacaoViagem.objects.create(
            data_viagem=timezone.now() + timedelta(days=5),
            data_fim_prevista=timezone.now() + timedelta(days=5, hours=4),
            quantidade_passageiros=30,
            local_embarque="Terminal A",
            local_desembarque="Terminal B",
            status='Pendente'
        )

    def test_pagina_gerenciar_viagem(self):
        response = self.client.get(reverse('solicitacao_viagem_gerenciar', args=[self.viagem.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Terminal A')

    def test_atribuir_veiculo_e_motorista(self):
        response = self.client.post(
            reverse('solicitacao_viagem_gerenciar', args=[self.viagem.id]),
            {'action': 'atribuir_veiculo', 'veiculo': self.veiculo.id_veiculo}
        )
        self.viagem.refresh_from_db()
        self.assertEqual(self.viagem.veiculo, self.veiculo)

        response = self.client.post(
            reverse('solicitacao_viagem_gerenciar', args=[self.viagem.id]),
            {'action': 'atribuir_solicitacao_motorista', 'solicitacao_motorista': self.solicitacao_motorista.id}
        )
        self.viagem.refresh_from_db()
        self.assertEqual(self.viagem.solicitacao_motorista, self.solicitacao_motorista)
        self.assertEqual(self.viagem.status, 'Confirmada')

    def test_cancelar_viagem(self):
        response = self.client.post(
            reverse('solicitacao_viagem_gerenciar', args=[self.viagem.id]),
            {'action': 'cancelar'}
        )
        self.viagem.refresh_from_db()
        self.assertEqual(self.viagem.status, 'Cancelada')

    def test_concluir_viagem(self):
        response = self.client.post(
            reverse('solicitacao_viagem_gerenciar', args=[self.viagem.id]),
            {'action': 'concluir'}
        )
        self.viagem.refresh_from_db()
        self.assertEqual(self.viagem.status, 'Concluida')
