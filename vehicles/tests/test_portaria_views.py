from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from vehicles.models import Motorista, Veiculo, SolicitacaoMotorista, SolicitacaoViagem, RegistroPortaria
from vehicles.tests.fixtures import criar_motorista, criar_veiculo, criar_solicitacao_motorista, criar_solicitacao_viagem


class PortariaViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.motorista = criar_motorista("Motorista Portaria", "D")
        self.veiculo = criar_veiculo("PORT001", "Mercedes-Benz", 44, kms_atual=1000)
        self.solicitacao_motorista = criar_solicitacao_motorista(
            motorista=self.motorista,
            status='Confirmada'
        )
        self.viagem = criar_solicitacao_viagem(
            veiculo=self.veiculo,
            solicitacao_motorista=self.solicitacao_motorista,
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

    def test_viagem_com_chegada_aparecem_concluidas(self):
        self.viagem.data_viagem = timezone.now()
        self.viagem.data_fim_prevista = timezone.now() + timedelta(hours=2)
        self.viagem.save()
        
        RegistroPortaria.objects.create(
            viagem=self.viagem,
            km_saida=1000,
            horario_saida=timezone.now(),
            km_chegada=1150,
            horario_chegada=timezone.now()
        )
        
        response = self.client.get(reverse('portaria_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Concluídas')

    def test_viagem_sem_chegada_aparecem_pendentes(self):
        response = self.client.get(reverse('portaria_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pendentes')

    def test_pagina_registrar_saida(self):
        response = self.client.get(reverse('portaria_registrar_saida', args=[self.viagem.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Registrar Saída')


class PortariaKmValidationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.motorista = Motorista.objects.create(
            nome="Motorista KM",
            tipo_carteira="D"
        )
        self.veiculo = Veiculo.objects.create(
            placa="KMVEIC01",
            marca="Scania",
            quantidade_passageiros=44,
            kms_atual=1000
        )
        self.solicitacao_motorista = SolicitacaoMotorista.objects.create(
            data_inicio=timezone.now() + timedelta(days=1),
            data_fim_prevista=timezone.now() + timedelta(days=1, hours=4),
            motorista=self.motorista,
            status='Confirmada'
        )
        self.viagem = SolicitacaoViagem.objects.create(
            data_viagem=timezone.now() + timedelta(days=1),
            data_fim_prevista=timezone.now() + timedelta(days=1, hours=4),
            quantidade_passageiros=40,
            local_embarque="A",
            local_desembarque="B",
            veiculo=self.veiculo,
            solicitacao_motorista=self.solicitacao_motorista,
            status='Confirmada'
        )

    def test_km_chegada_menor_saida_retorna_erro(self):
        RegistroPortaria.objects.create(
            viagem=self.viagem,
            km_saida=1000,
            horario_saida=timezone.now()
        )

        response = self.client.post(
            reverse('portaria_registrar_chegada', args=[self.viagem.id]),
            {'km_chegada': '500', 'observacao_chegada': 'Teste'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('não pode ser menor', response.content.decode())

    def test_km_chegada_igual_saida_sucesso(self):
        RegistroPortaria.objects.create(
            viagem=self.viagem,
            km_saida=1000,
            horario_saida=timezone.now()
        )

        response = self.client.post(
            reverse('portaria_registrar_chegada', args=[self.viagem.id]),
            {'km_chegada': '1000', 'observacao_chegada': 'Chegada'}
        )

        self.assertRedirects(response, reverse('portaria_list'))

    def test_km_chegada_maior_saida_sucesso(self):
        RegistroPortaria.objects.create(
            viagem=self.viagem,
            km_saida=1000,
            horario_saida=timezone.now()
        )

        response = self.client.post(
            reverse('portaria_registrar_chegada', args=[self.viagem.id]),
            {'km_chegada': '1150', 'observacao_chegada': 'Chegada'}
        )

        self.assertRedirects(response, reverse('portaria_list'))
        self.veiculo.refresh_from_db()
        self.assertEqual(self.veiculo.kms_atual, 1150)

    def test_registrar_chegada_sem_km_retorna_erro(self):
        RegistroPortaria.objects.create(
            viagem=self.viagem,
            km_saida=1000,
            horario_saida=timezone.now()
        )

        response = self.client.post(
            reverse('portaria_registrar_chegada', args=[self.viagem.id]),
            {'km_chegada': '', 'observacao_chegada': ''}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'obrigatório')
