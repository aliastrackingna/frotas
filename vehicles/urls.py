from django.urls import path
from . import views

urlpatterns = [
    path('', views.veiculo_list, name='veiculo_list'),
    path('<int:pk>/', views.veiculo_detail, name='veiculo_detail'),
    path('novo/', views.veiculo_create, name='veiculo_create'),
    path('<int:pk>/editar/', views.veiculo_update, name='veiculo_update'),
    path('<int:pk>/excluir/', views.veiculo_delete, name='veiculo_delete'),
    path('<int:veiculo_pk>/observacao/', views.observacao_create, name='observacao_create'),
]
