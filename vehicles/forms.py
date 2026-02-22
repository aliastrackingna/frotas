from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime
from .models import Veiculo, Motorista, SolicitacaoMotorista, SolicitacaoViagem, Observacao, RegistroPortaria


class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = ['placa', 'marca', 'modelo', 'quantidade_passageiros', 'km_inicial', 'kms_atual']
        widgets = {
            'placa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ABC-1234'}),
            'marca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Toyota'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Corolla'}),
            'quantidade_passageiros': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'km_inicial': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'kms_atual': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

    def clean_placa(self):
        placa = self.cleaned_data.get('placa', '').upper().strip()
        if len(placa) < 7:
            raise ValidationError('Placa deve ter pelo menos 7 caracteres')
        return placa


class MotoristaForm(forms.ModelForm):
    class Meta:
        model = Motorista
        fields = ['nome', 'tipo_carteira']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'João Silva'}),
            'tipo_carteira': forms.Select(attrs={'class': 'form-control'}),
        }


class ObservacaoForm(forms.ModelForm):
    class Meta:
        model = Observacao
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Digite a observação...'
            }),
        }

    def clean_texto(self):
        texto = self.cleaned_data.get('texto', '').strip()
        if not texto:
            raise ValidationError('Observação não pode estar vazia')
        return texto


class SolicitacaoMotoristaForm(forms.ModelForm):
    data_inicio_data = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Data de Início'
    )
    data_inicio_hora = forms.ChoiceField(
        choices=[('', 'Selecione')] + [(f'{h:02d}:{m:02d}', f'{h:02d}:{m:02d}') for h in range(24) for m in [0, 30]],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Hora de Início'
    )
    data_fim_prevista_data = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Data de Retorno'
    )
    data_fim_prevista_hora = forms.ChoiceField(
        choices=[('', 'Selecione')] + [(f'{h:02d}:{m:02d}', f'{h:02d}:{m:02d}') for h in range(24) for m in [0, 30]],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Hora de Retorno'
    )

    class Meta:
        model = SolicitacaoMotorista
        fields = ['observacao']
        widgets = {
            'observacao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações adicionais...'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        data_inicio_data = cleaned_data.get('data_inicio_data')
        data_inicio_hora = cleaned_data.get('data_inicio_hora')
        data_fim_prevista_data = cleaned_data.get('data_fim_prevista_data')
        data_fim_prevista_hora = cleaned_data.get('data_fim_prevista_hora')

        if not data_inicio_data or not data_inicio_hora:
            raise ValidationError('Data e hora de início são obrigatórios')

        if not data_fim_prevista_data or not data_fim_prevista_hora:
            raise ValidationError('Data e hora de retorno são obrigatórios')

        try:
            data_inicio = datetime.combine(data_inicio_data, datetime.strptime(data_inicio_hora, '%H:%M').time())
            data_inicio = timezone.make_aware(data_inicio)
        except (ValueError, TypeError):
            raise ValidationError('Data de início inválida')

        try:
            data_fim = datetime.combine(data_fim_prevista_data, datetime.strptime(data_fim_prevista_hora, '%H:%M').time())
            data_fim = timezone.make_aware(data_fim)
        except (ValueError, TypeError):
            raise ValidationError('Data de retorno inválida')

        if data_inicio < timezone.now():
            raise ValidationError('A data de início não pode ser no passado')

        if data_fim <= data_inicio:
            raise ValidationError('A data de retorno deve ser posterior à data de início')

        cleaned_data['data_inicio'] = data_inicio
        cleaned_data['data_fim_prevista'] = data_fim

        return cleaned_data


class SolicitacaoViagemForm(forms.ModelForm):
    data_viagem_data = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Data da Viagem'
    )
    data_viagem_hora = forms.ChoiceField(
        choices=[('', 'Selecione')] + [(f'{h:02d}:{m:02d}', f'{h:02d}:{m:02d}') for h in range(24) for m in [0, 30]],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Hora da Viagem'
    )
    data_fim_prevista_data = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Data de Retorno'
    )
    data_fim_prevista_hora = forms.ChoiceField(
        choices=[('', 'Selecione')] + [(f'{h:02d}:{m:02d}', f'{h:02d}:{m:02d}') for h in range(24) for m in [0, 30]],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Hora de Retorno'
    )

    class Meta:
        model = SolicitacaoViagem
        fields = ['quantidade_passageiros', 'local_embarque', 'local_desembarque', 'observacao']
        widgets = {
            'quantidade_passageiros': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'local_embarque': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Local de Embarque'}),
            'local_desembarque': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Local de Desembarque'}),
            'observacao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações adicionais...'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        data_viagem_data = cleaned_data.get('data_viagem_data')
        data_viagem_hora = cleaned_data.get('data_viagem_hora')
        data_fim_prevista_data = cleaned_data.get('data_fim_prevista_data')
        data_fim_prevista_hora = cleaned_data.get('data_fim_prevista_hora')

        if not data_viagem_data or not data_viagem_hora:
            raise ValidationError('Data e hora da viagem são obrigatórios')

        if not data_fim_prevista_data or not data_fim_prevista_hora:
            raise ValidationError('Data e hora de retorno são obrigatórios')

        try:
            data_viagem = datetime.combine(data_viagem_data, datetime.strptime(data_viagem_hora, '%H:%M').time())
            data_viagem = timezone.make_aware(data_viagem)
        except (ValueError, TypeError):
            raise ValidationError('Data da viagem inválida')

        try:
            data_fim = datetime.combine(data_fim_prevista_data, datetime.strptime(data_fim_prevista_hora, '%H:%M').time())
            data_fim = timezone.make_aware(data_fim)
        except (ValueError, TypeError):
            raise ValidationError('Data de retorno inválida')

        if data_viagem < timezone.now():
            raise ValidationError('A data da viagem não pode ser no passado')

        if data_fim <= data_viagem:
            raise ValidationError('A data de retorno deve ser posterior à data da viagem')

        cleaned_data['data_viagem'] = data_viagem
        cleaned_data['data_fim_prevista'] = data_fim

        return cleaned_data


class RegistroPortariaSaidaForm(forms.ModelForm):
    class Meta:
        model = RegistroPortaria
        fields = ['km_saida', 'observacao_saida']
        widgets = {
            'km_saida': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'KM de saída'
            }),
            'observacao_saida': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observações na saída...'
            }),
        }


class RegistroPortariaChegadaForm(forms.ModelForm):
    class Meta:
        model = RegistroPortaria
        fields = ['km_chegada', 'observacao_chegada']
        widgets = {
            'km_chegada': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'KM de chegada'
            }),
            'observacao_chegada': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observações na chegada...'
            }),
        }

    def clean_km_chegada(self):
        km_chegada = self.cleaned_data.get('km_chegada')
        if not km_chegada:
            raise ValidationError('KM de chegada é obrigatório')
        return km_chegada
