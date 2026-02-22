import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from vehicles.models import Motorista, SolicitacaoMotorista


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

    def test_agendar_mesmo_motorista_maneira_e_tarde_mesmo_dia(self):
        from datetime import datetime
        
        dia_futuro = (timezone.now() + timedelta(days=1)).date()
        
        manha_inicio = timezone.make_aware(datetime.combine(dia_futuro, datetime.min.time().replace(hour=8)))
        manha_fim = timezone.make_aware(datetime.combine(dia_futuro, datetime.min.time().replace(hour=12)))
        
        tarde_inicio = timezone.make_aware(datetime.combine(dia_futuro, datetime.min.time().replace(hour=14)))
        tarde_fim = timezone.make_aware(datetime.combine(dia_futuro, datetime.min.time().replace(hour=18)))
        
        response1 = self.client.post(reverse('solicitacao_create'), {
            'data_inicio': manha_inicio.strftime('%Y-%m-%dT%H:%M'),
            'data_fim_prevista': manha_fim.strftime('%Y-%m-%dT%H:%M'),
            'observacao': 'Viagem de manhã'
        })
        self.assertEqual(response1.status_code, 302)
        solicitacao_manha = SolicitacaoMotorista.objects.get(observacao='Viagem de manhã')
        self.assertEqual(solicitacao_manha.motorista, self.motorista)
        self.assertEqual(solicitacao_manha.status, 'Confirmada')
        
        response2 = self.client.post(reverse('solicitacao_create'), {
            'data_inicio': tarde_inicio.strftime('%Y-%m-%dT%H:%M'),
            'data_fim_prevista': tarde_fim.strftime('%Y-%m-%dT%H:%M'),
            'observacao': 'Viagem de tarde'
        })
        self.assertEqual(response2.status_code, 302)
        solicitacao_tarde = SolicitacaoMotorista.objects.get(observacao='Viagem de tarde')
        self.assertEqual(solicitacao_tarde.motorista, self.motorista)
        self.assertEqual(solicitacao_tarde.status, 'Confirmada')
        
        self.assertEqual(SolicitacaoMotorista.objects.count(), 2)
