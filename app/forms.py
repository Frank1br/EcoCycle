from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
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
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control mb-2'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Padronização total dos Placeholders do Cadastro
        self.fields['username'].widget.attrs.update({'placeholder': 'Digite seu usuário'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Digite seu e-mail'})
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Digite seu nome'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Digite seu sobrenome'})
        
        # Adiciona placeholders também para as senhas geradas pelo UserCreationForm
        if 'password_1' in self.fields:
            self.fields['password_1'].widget.attrs.update({'placeholder': 'Digite sua senha'})
        if 'password_2' in self.fields:
            self.fields['password_2'].widget.attrs.update({'placeholder': 'Confirme sua senha'})

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