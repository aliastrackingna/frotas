from django.test import TestCase, Client
from django.urls import reverse
from vehicles.models import Veiculo, Observacao


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
