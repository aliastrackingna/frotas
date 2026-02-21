from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('list/', views.veiculo_list, name='veiculo_list'),
    path('novo/', views.veiculo_create, name='veiculo_create'),
    path('<int:pk>/', views.veiculo_detail, name='veiculo_detail'),
    path('<int:pk>/editar/', views.veiculo_update, name='veiculo_update'),
    path('<int:pk>/excluir/', views.veiculo_delete, name='veiculo_delete'),
    path('<int:veiculo_pk>/observacao/', views.observacao_create, name='observacao_create'),
]
