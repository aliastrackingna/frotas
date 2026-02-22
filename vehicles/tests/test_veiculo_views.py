import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from vehicles.models import Veiculo


class VeiculoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.veiculo = Veiculo.objects.create(
            placa='TEST1234',
            marca='Volkswagen',
            quantidade_passageiros=15,
            km_inicial=1000,
            kms_atual=1500
        )

    def test_index(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Veículos')
        self.assertContains(response, '1')

    def test_listar_veiculos(self):
        response = self.client.get(reverse('veiculo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TEST1234')

    def test_detalhes_veiculo(self):
        response = self.client.get(reverse('veiculo_detail', args=[self.veiculo.id_veiculo]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TEST1234')
        self.assertContains(response, 'Volkswagen')

    def test_pagina_criar_veiculo(self):
        response = self.client.get(reverse('veiculo_create'))
        self.assertEqual(response.status_code, 200)

    def test_criar_veiculo(self):
        response = self.client.post(reverse('veiculo_create'), {
            'placa': 'NOVO5678',
            'marca': 'Ford',
            'quantidade_passageiros': '7',
            'km_inicial': '500',
            'kms_atual': '500'
        })
        self.assertRedirects(response, reverse('veiculo_list'))
        self.assertEqual(Veiculo.objects.filter(placa='NOVO5678').count(), 1)

    def test_pagina_editar_veiculo(self):
        response = self.client.get(reverse('veiculo_update', args=[self.veiculo.id_veiculo]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TEST1234')

    def test_editar_veiculo(self):
        response = self.client.post(reverse('veiculo_update', args=[self.veiculo.id_veiculo]), {
            'placa': 'TEST1234',
            'marca': 'Chevrolet',
            'quantidade_passageiros': '9',
            'km_inicial': '1000',
            'kms_atual': '2000'
        })
        self.assertRedirects(response, reverse('veiculo_list'))
        self.veiculo.refresh_from_db()
        self.assertEqual(self.veiculo.marca, 'Chevrolet')

    def test_pagina_excluir_veiculo(self):
        response = self.client.get(reverse('veiculo_delete', args=[self.veiculo.id_veiculo]))
        self.assertEqual(response.status_code, 200)

    def test_excluir_veiculo(self):
        veiculo_id = self.veiculo.id_veiculo
        response = self.client.post(reverse('veiculo_delete', args=[veiculo_id]))
        self.assertRedirects(response, reverse('veiculo_list'))
        self.assertFalse(Veiculo.objects.filter(id_veiculo=veiculo_id).exists())
