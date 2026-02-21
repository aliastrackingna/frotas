from django.contrib import admin
from .models import Veiculo, Observacao


class ObservacaoInline(admin.TabularInline):
    model = Observacao
    extra = 0
    readonly_fields = ['data_criacao']


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ['placa', 'marca', 'quantidade_passageiros', 'km_inicial', 'kms_atual']
    search_fields = ['placa', 'marca']
    inlines = [ObservacaoInline]


@admin.register(Observacao)
class ObservacaoAdmin(admin.ModelAdmin):
    list_display = ['veiculo', 'texto', 'data_criacao']
    list_filter = ['data_criacao']
    search_fields = ['texto', 'veiculo__placa']
    readonly_fields = ['data_criacao']
