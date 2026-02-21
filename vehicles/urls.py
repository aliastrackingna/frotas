from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('motoristas/', views.motorista_list, name='motorista_list'),
    path('motoristas/novo/', views.motorista_create, name='motorista_create'),
    path('motoristas/<int:pk>/', views.motorista_detail, name='motorista_detail'),
    path('motoristas/<int:pk>/editar/', views.motorista_update, name='motorista_update'),
    path('motoristas/<int:pk>/excluir/', views.motorista_delete, name='motorista_delete'),
    path('solicitacoes/', views.solicitacao_list, name='solicitacao_list'),
    path('solicitacoes/nova/', views.solicitacao_create, name='solicitacao_create'),
    path('solicitacoes/<int:pk>/', views.solicitacao_detail, name='solicitacao_detail'),
    path('solicitacoes/gerenciar/<int:pk>/', views.solicitacao_gerenciar, name='solicitacao_gerenciar'),
    path('solicitacoes/viagem/', views.solicitacao_viagem_list, name='solicitacao_viagem_list'),
    path('solicitacoes/viagem/nova/', views.solicitacao_viagem_create, name='solicitacao_viagem_create'),
    path('solicitacoes/viagem/<int:pk>/', views.solicitacao_viagem_detail, name='solicitacao_viagem_detail'),
    path('solicitacoes/viagem/gerenciar/<int:pk>/', views.solicitacao_viagem_gerenciar, name='solicitacao_viagem_gerenciar'),
    path('list/', views.veiculo_list, name='veiculo_list'),
    path('novo/', views.veiculo_create, name='veiculo_create'),
    path('<int:pk>/', views.veiculo_detail, name='veiculo_detail'),
    path('<int:pk>/editar/', views.veiculo_update, name='veiculo_update'),
    path('<int:pk>/excluir/', views.veiculo_delete, name='veiculo_delete'),
    path('<int:veiculo_pk>/observacao/', views.observacao_create, name='observacao_create'),
]
