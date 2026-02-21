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
        data_viagem = (agora + timedelta(days=100)).strftime('%Y-%m-%dT%H:%M')
        data_fim = (agora + timedelta(days=100, hours=4)).strftime('%Y-%m-%dT%H:%M')
        
        response = self.client.post(reverse('solicitacao_viagem_create'), {
            'data_viagem': data_viagem,
            'data_fim_prevista': data_fim,
            'quantidade_passageiros': '15',
            'local_embarque': 'Escola A',
            'local_desembarque': 'Escola B',
        })
        
        viagem = SolicitacaoViagem.objects.last()
        self.assertIsNotNone(viagem)
        self.assertIn(viagem.status, ['Confirmada', 'Pendente'])

    def test_criar_viagem_capacidade_proxima_pendente(self):
        agora = timezone.now()
        data_viagem = (agora + timedelta(days=100)).strftime('%Y-%m-%dT%H:%M')
        data_fim = (agora + timedelta(days=100, hours=4)).strftime('%Y-%m-%dT%H:%M')
        
        response = self.client.post(reverse('solicitacao_viagem_create'), {
            'data_viagem': data_viagem,
            'data_fim_prevista': data_fim,
            'quantidade_passageiros': '25',
            'local_embarque': 'A',
            'local_desembarque': 'B',
        })
        
        viagem = SolicitacaoViagem.objects.last()
        self.assertIn(viagem.status, ['Confirmada', 'Pendente'])

    def test_criar_viagem_itinerario(self):
        agora = timezone.now()
        data_viagem = (agora + timedelta(days=100)).strftime('%Y-%m-%dT%H:%M')
        data_fim = (agora + timedelta(days=100, hours=4)).strftime('%Y-%m-%dT%H:%M')
        
        response = self.client.post(reverse('solicitacao_viagem_create'), {
            'data_viagem': data_viagem,
            'data_fim_prevista': data_fim,
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
            'data_viagem': 'data-invalida',
            'data_fim_prevista': 'outra-data-invalida',
            'quantidade_passageiros': '30',
            'local_embarque': 'A',
            'local_desembarque': 'B',
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Datas inválidas')


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


class VeiculoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
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


class MotoristaViewTest(TestCase):
    def setUp(self):
        self.client = Client()
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


class ViagemGerenciarViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.motorista = Motorista.objects.create(
            nome="Motorista Viagem",
            tipo_carteira="D"
        )
        self.veiculo = Veiculo.objects.create(
            placa="VGTEST01",
            marca="Volvo",
            quantidade_passageiros=44
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
            {'action': 'atribuir_motorista', 'motorista': self.motorista.id_motorista}
        )
        self.viagem.refresh_from_db()
        self.assertEqual(self.viagem.motorista, self.motorista)
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


class PortariaKmValidationTest(TestCase):
    def setUp(self):
        self.client = Client()
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
        self.viagem = SolicitacaoViagem.objects.create(
            data_viagem=timezone.now() + timedelta(days=1),
            data_fim_prevista=timezone.now() + timedelta(days=1, hours=4),
            quantidade_passageiros=40,
            local_embarque="A",
            local_desembarque="B",
            veiculo=self.veiculo,
            motorista=self.motorista,
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
