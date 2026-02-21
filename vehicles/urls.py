from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VeiculoViewSet, ObservacaoViewSet

router = DefaultRouter()
router.register(r'veiculos', VeiculoViewSet)
router.register(r'observacoes', ObservacaoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
