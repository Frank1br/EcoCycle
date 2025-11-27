from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import Contato, Pedido

# Mixin para adicionar classes Bootstrap padrão
class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            # Adiciona a classe form-control e espaçamento inferior
            self.fields[field].widget.attrs.update({'class': 'form-control mb-2'})

class ContatoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Contato
        fields = ['nome', 'email', 'mensagem']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Digite seu nome'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Digite seu e-mail'}),
            'mensagem': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Digite sua mensagem'}),
        }

class CadastroForm(BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control mb-2'}),
        help_text='Digite um e-mail válido. Será usado para login.'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customiza o campo username para aceitar espaços
        self.fields['username'].validators = [
            RegexValidator(
                regex=r'^[\w\s.@+-]+$',
                message='Nome de usuário pode conter letras, números, espaços e os caracteres @/./+/-/_',
                code='invalid_username'
            )
        ]
        self.fields['username'].help_text = 'Obrigatório. 150 caracteres ou menos. Letras, números, espaços e @/./+/-/_ apenas.'
        self.fields['username'].label = 'Nome Completo'

        # Customiza o campo de email
        self.fields['email'].label = 'Email'

        # Padronização dos Placeholders do Cadastro
        self.fields['username'].widget.attrs.update({'placeholder': 'Digite seu nome completo'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Digite seu e-mail'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Digite sua senha'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirme sua senha'})

    def clean_email(self):
        """
        Valida se o email já está cadastrado no sistema
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este email já está cadastrado. Por favor, use outro email ou faça login.')
        return email

    def clean_username(self):
        """
        Valida e limpa o username, permitindo espaços
        """
        username = self.cleaned_data.get('username')
        # Remove espaços duplicados e espaços nas pontas
        username = ' '.join(username.split())
        return username

class PedidoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['quantidade']
        widgets = {
            'quantidade': forms.NumberInput(attrs={'placeholder': '0'})
        }

# Formulário de Login Personalizado
# Este é o segredo para os placeholders aparecerem na tela de login!
class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Digite seu usuário'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Digite sua senha'
        })