from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from vehicles.models import Motorista


class MotoristaViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.motorista = Motorista.objects.create(
            nome='João Silva',
            tipo_carteira='D'
        )

    def test_listar_motoristas(self):
        response = self.client.get(reverse('motorista_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'João Silva')

    def test_detalhes_motorista(self):
        response = self.client.get(reverse('motorista_detail', args=[self.motorista.id_motorista]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'João Silva')

    def test_pagina_criar_motorista(self):
        response = self.client.get(reverse('motorista_create'))
        self.assertEqual(response.status_code, 200)

    def test_criar_motorista(self):
        response = self.client.post(reverse('motorista_create'), {
            'nome': 'Maria Oliveira',
            'tipo_carteira': 'B'
        })
        self.assertRedirects(response, reverse('motorista_list'))
        self.assertEqual(Motorista.objects.filter(nome='Maria Oliveira').count(), 1)

    def test_pagina_editar_motorista(self):
        response = self.client.get(reverse('motorista_update', args=[self.motorista.id_motorista]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'João Silva')

    def test_editar_motorista(self):
        response = self.client.post(reverse('motorista_update', args=[self.motorista.id_motorista]), {
            'nome': 'João Santos',
            'tipo_carteira': 'E'
        })
        self.assertRedirects(response, reverse('motorista_list'))
        self.motorista.refresh_from_db()
        self.assertEqual(self.motorista.nome, 'João Santos')
        self.assertEqual(self.motorista.tipo_carteira, 'E')

    def test_pagina_excluir_motorista(self):
        response = self.client.get(reverse('motorista_delete', args=[self.motorista.id_motorista]))
        self.assertEqual(response.status_code, 200)

    def test_excluir_motorista(self):
        motorista_id = self.motorista.id_motorista
        response = self.client.post(reverse('motorista_delete', args=[motorista_id]))
        self.assertRedirects(response, reverse('motorista_list'))
        self.assertFalse(Motorista.objects.filter(id_motorista=motorista_id).exists())
