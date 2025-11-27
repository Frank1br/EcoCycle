# Documentação Técnica - EcoCycle

## Sumário
1. [Arquitetura do Sistema](#arquitetura-do-sistema)
2. [Fluxo de Autenticação](#fluxo-de-autenticação)
3. [API de Views](#api-de-views)
4. [Formulários e Validações](#formulários-e-validações)
5. [Middleware Customizado](#middleware-customizado)
6. [Templates e Frontend](#templates-e-frontend)
7. [Banco de Dados](#banco-de-dados)
8. [Boas Práticas Implementadas](#boas-práticas-implementadas)

---

## Arquitetura do Sistema

### Padrão MVT (Model-View-Template)

O projeto segue o padrão MVT do Django:

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Browser   │─────▶│    View     │─────▶│    Model    │
│  (Client)   │◀─────│ (Controller)│◀─────│   (Data)    │
└─────────────┘      └─────────────┘      └─────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │  Template   │
                     │    (UI)     │
                     └─────────────┘
```

### Estrutura de Camadas

```
Presentation Layer (Templates)
    ├── base.html (template mestre)
    ├── index.html
    ├── login.html / admin_login.html
    └── ...

Business Logic Layer (Views + Forms)
    ├── views.py (8 views)
    ├── forms.py (4 forms)
    └── middleware.py (1 middleware)

Data Layer (Models)
    ├── models.py (4 models)
    └── migrations/

Configuration Layer
    ├── settings.py
    └── urls.py
```

---

## Fluxo de Autenticação

### Diagrama de Fluxo

```
┌──────────────────────────────────────────────────────────────┐
│                     Acesso ao Sistema                         │
└───────────────────┬──────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
  ┌─────▼─────┐         ┌──────▼──────┐
  │   /login/ │         │/admin-login/│
  │  (Site)   │         │   (Admin)   │
  └─────┬─────┘         └──────┬──────┘
        │                      │
        ▼                      ▼
  site_login()           admin_login()
        │                      │
        ├── Valida             ├── Valida is_staff
        ├── Autentica          ├── Autentica
        └── session['auth_type']='site'
                               └── session['auth_type']='admin'
        │                      │
        ▼                      ▼
    index/                 /admin/
```

### Middleware de Separação

**Localização:** `app/middleware.py`

**Funcionamento:**

1. **Intercepta todas as requisições**
   ```python
   def __call__(self, request):
       url_name = resolve(request.path_info).url_name
       is_admin_area = request.path.startswith('/admin/')
   ```

2. **Detecta área acessada**
   - Admin: `/admin/`, `/admin-login/`
   - Site: Todas as outras rotas

3. **Verifica tipo de sessão**
   ```python
   session_type = request.session.get('auth_type', 'site')
   ```

4. **Aplica regras de separação**
   ```python
   if is_admin_area and session_type == 'site':
       logout(request)  # Incompatível!
   ```

### Estados de Sessão

| Estado | Pode Acessar Site | Pode Acessar Admin |
|--------|-------------------|-------------------|
| Não autenticado | ✅ (público) | ❌ (redirect login) |
| auth_type='site' | ✅ | ❌ (logout + redirect) |
| auth_type='admin' | ❌ (logout + redirect) | ✅ |

---

## API de Views

### 1. `index(request)`
**Rota:** `/`
**Método:** `GET`, `POST`
**Autenticação:** Não requerida

**Funcionalidade:**
- Lista produtos com estoque disponível
- Processa formulário de contato
- Renderiza hero section com conteúdo dinâmico

**Código:**
```python
def index(request):
    pagina = Pagina.objects.first()
    produtos = Produto.objects.filter(estoque__gt=0)

    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mensagem enviada!')
            return redirect('index')
    else:
        form = ContatoForm()

    context = {
        'pagina': pagina,
        'produtos': produtos,
        'form_contato': form
    }
    return render(request, 'index.html', context)
```

### 2. `cadastro(request)`
**Rota:** `/cadastro/`
**Método:** `GET`, `POST`
**Autenticação:** Não requerida

**Funcionalidade:**
- Registra novos usuários
- Valida email único
- Aceita espaços no username (nome completo)
- Login automático após cadastro
- Define `auth_type='site'`

**Validações:**
```python
# forms.py - CadastroForm
def clean_email(self):
    email = self.cleaned_data.get('email')
    if User.objects.filter(email=email).exists():
        raise ValidationError('Este email já está cadastrado.')
    return email

def clean_username(self):
    username = self.cleaned_data.get('username')
    return ' '.join(username.split())  # Remove espaços extras
```

### 3. `site_login(request)`
**Rota:** `/login/`
**Método:** `GET`, `POST`
**Autenticação:** Não requerida

**Funcionalidade:**
- Login de usuários do site
- Define sessão do tipo 'site'
- Redirect para usuários já autenticados

**Fluxo:**
```python
def site_login(request):
    # 1. Verifica se já está autenticado como 'site'
    if request.user.is_authenticated and request.session.get('auth_type') == 'site':
        return redirect('index')

    # 2. Processa POST
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(...)
            if user is not None:
                login(request, user)
                request.session['auth_type'] = 'site'  # CRÍTICO
                return redirect('index')

    # 3. Renderiza formulário
    return render(request, 'registration/login.html', {'form': form})
```

### 4. `admin_login(request)`
**Rota:** `/admin-login/`
**Método:** `GET`, `POST`
**Autenticação:** Requer `is_staff=True`

**Funcionalidade:**
- Login exclusivo para administradores
- Valida permissão `is_staff`
- Define sessão do tipo 'admin'
- Mensagem de erro para não-admins

**Validação de Permissão:**
```python
def admin_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(...)

            # VALIDAÇÃO CRÍTICA
            if user is not None and user.is_staff:
                login(request, user)
                request.session['auth_type'] = 'admin'
                return redirect('/admin/')
            else:
                messages.error(request, 'Acesso negado. Apenas administradores.')
```

### 5. `comprar(request, produto_id)`
**Rota:** `/comprar/<id>/`
**Método:** `GET`, `POST`
**Autenticação:** ✅ Requerida (`@login_required`)

**Funcionalidade:**
- Exibe detalhes do produto
- Processa compra
- Valida estoque disponível
- Atualiza estoque
- Cria registro de pedido

**Validações:**
```python
@login_required
def comprar(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)

    if request.method == 'POST':
        qtd = int(request.POST.get('quantidade', 1))

        # Validação de estoque
        if qtd > produto.estoque:
            messages.error(request, 'Estoque insuficiente.')
        elif qtd <= 0:
            messages.error(request, 'Quantidade inválida.')
        else:
            # Cria pedido
            Pedido.objects.create(
                usuario=request.user,
                produto=produto,
                quantidade=qtd,
                total=produto.preco * qtd
            )

            # Atualiza estoque
            produto.estoque -= qtd
            produto.save()

            messages.success(request, 'Compra realizada!')
            return redirect('perfil')
```

### 6. `perfil(request)`
**Rota:** `/perfil/`
**Método:** `GET`
**Autenticação:** ✅ Requerida

**Funcionalidade:**
- Exibe histórico de pedidos do usuário
- Ordenação por data (mais recentes primeiro)

```python
@login_required
def perfil(request):
    pedidos = Pedido.objects.filter(
        usuario=request.user
    ).order_by('-data')
    return render(request, 'perfil.html', {'pedidos': pedidos})
```

---

## Formulários e Validações

### 1. CadastroForm
**Herança:** `UserCreationForm`

**Campos Customizados:**
```python
class CadastroForm(BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
```

**Customizações:**

#### Username com Espaços
```python
self.fields['username'].validators = [
    RegexValidator(
        regex=r'^[\w\s.@+-]+$',
        message='Nome pode conter espaços'
    )
]
self.fields['username'].label = 'Nome Completo'
```

#### Validação de Email Único
```python
def clean_email(self):
    email = self.cleaned_data.get('email')
    if User.objects.filter(email=email).exists():
        raise ValidationError(
            'Este email já está cadastrado. '
            'Por favor, use outro email ou faça login.'
        )
    return email
```

#### Limpeza de Username
```python
def clean_username(self):
    username = self.cleaned_data.get('username')
    # Remove espaços duplicados e nas pontas
    return ' '.join(username.split())
```

### 2. LoginForm
**Herança:** `AuthenticationForm`

**Customização:**
```python
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
```

### 3. ContatoForm
**Campos:** nome, email, mensagem

```python
class ContatoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Contato
        fields = ['nome', 'email', 'mensagem']
        widgets = {
            'nome': forms.TextInput(attrs={
                'placeholder': 'Digite seu nome'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Digite seu e-mail'
            }),
            'mensagem': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Digite sua mensagem'
            }),
        }
```

### BootstrapFormMixin
**Utilidade:** Adiciona classes Bootstrap automaticamente

```python
class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control mb-2'
            })
```

---

## Middleware Customizado

### SeparateAdminAuthMiddleware

**Arquivo:** `app/middleware.py`

**Objetivo:** Manter sessões completamente separadas entre admin e site.

**Implementação Completa:**

```python
from django.contrib.auth import logout
from django.urls import resolve

class SeparateAdminAuthMiddleware:
    """
    Middleware que mantém sessões separadas entre admin e site.

    Casos de uso:
    1. Usuário faz login no site → não pode acessar /admin/
    2. Admin faz login no painel → não pode acessar site como usuário
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Detecta área da requisição
        url_name = resolve(request.path_info).url_name
        url_namespace = resolve(request.path_info).namespace

        is_admin_area = (
            request.path.startswith('/admin/') or
            url_name == 'admin_login' or
            url_namespace == 'admin'
        )

        # 2. Marca no request
        request.is_admin_area = is_admin_area

        # 3. Verifica conflito de sessão
        if request.user.is_authenticated:
            session_type = request.session.get('auth_type', 'site')

            # Conflito: usuário 'site' tentando acessar admin
            if is_admin_area and session_type == 'site':
                logout(request)

            # Conflito: admin tentando acessar site
            elif not is_admin_area and session_type == 'admin':
                logout(request)

        response = self.get_response(request)
        return response
```

**Registro no settings.py:**
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'app.middleware.SeparateAdminAuthMiddleware',  # ← AQUI
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

**Importante:** O middleware deve estar **APÓS** `AuthenticationMiddleware` para ter acesso a `request.user`.

---

## Templates e Frontend

### Hierarquia de Templates

```
base.html (Template Mestre)
    ├── Define: navbar, footer, messages, CSS global
    └── Block: {% block content %}{% endblock %}
        │
        ├── index.html (Hero + Produtos + Contato)
        ├── login.html (Login site + botão admin)
        ├── cadastro.html (Registro de usuários)
        ├── comprar.html (Detalhes + Compra)
        ├── perfil.html (Dashboard + Pedidos)
        └── admin_login.html (Login administrativo)
```

### Design System

#### Variáveis CSS
```css
:root {
    /* Cores Principais */
    --primary-dark: #0F172A;
    --primary-green: #10B981;
    --primary-green-hover: #059669;
    --secondary-bg: #E2E8F0;
    --text-dark: #1E293B;
    --text-light: #64748B;
    --white: #FFFFFF;
    --border-light: #CBD5E1;

    /* Utilidades */
    --danger: #EF4444;
    --warning: #F59E0B;
    --success: #10B981;

    /* Sombras */
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
    --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
    --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);

    /* Bordas */
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;

    /* Espaçamento */
    --spacing-xs: 0.5rem;
    --spacing-sm: 1rem;
    --spacing-md: 1.5rem;
    --spacing-lg: 2rem;
}
```

#### Componentes Reutilizáveis

**Card de Produto:**
```html
<div class="product-card">
    <div class="product-image">
        <img src="{{ produto.foto.url }}" alt="{{ produto.nome }}">
        <span class="product-badge">{{ produto.estoque }} disponíveis</span>
    </div>
    <div class="product-body">
        <h3>{{ produto.nome }}</h3>
        <p>{{ produto.descricao|truncatewords:15 }}</p>
        <div class="product-footer">
            <span class="product-price">R$ {{ produto.preco }}</span>
            <a href="{% url 'comprar' produto.id %}" class="btn-product">
                Comprar
            </a>
        </div>
    </div>
</div>
```

**Botão Primário:**
```css
.btn-primary {
    background: linear-gradient(135deg, var(--primary-green) 0%, var(--primary-green-hover) 100%);
    color: var(--white);
    padding: 0.75rem 1.5rem;
    border-radius: var(--radius-sm);
    border: none;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}
```

### Responsividade

**Estratégia Mobile-First:**

```css
/* Mobile (base) */
.product-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
}

/* Tablet */
@media (min-width: 768px) {
    .product-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 1.5rem;
    }
}

/* Desktop */
@media (min-width: 992px) {
    .product-grid {
        grid-template-columns: repeat(3, 1fr);
        gap: 2rem;
    }
}
```

---

## Banco de Dados

### Diagrama ER

```
┌─────────────────┐
│      User       │ (Django padrão)
│─────────────────│
│ id (PK)         │
│ username        │◄────┐
│ email           │     │
│ password        │     │
│ is_staff        │     │
└─────────────────┘     │
                        │ FK
┌─────────────────┐     │
│     Pedido      │     │
│─────────────────│     │
│ id (PK)         │     │
│ usuario_id (FK) │─────┘
│ produto_id (FK) │─────┐
│ quantidade      │     │
│ total           │     │
│ data            │     │
└─────────────────┘     │
                        │ FK
┌─────────────────┐     │
│    Produto      │◄────┘
│─────────────────│
│ id (PK)         │
│ nome            │
│ descricao       │
│ preco           │
│ estoque         │
│ foto            │
│ data_adicao     │
└─────────────────┘

┌─────────────────┐
│     Pagina      │
│─────────────────│
│ id (PK)         │
│ titulo          │
│ subtitulo       │
│ descricao       │
│ logo_do_site    │
│ imagem_sobre    │
└─────────────────┘

┌─────────────────┐
│    Contato      │
│─────────────────│
│ id (PK)         │
│ nome            │
│ email           │
│ mensagem        │
│ data_envio      │
└─────────────────┘
```

### Relacionamentos

```python
# Pedido → User (Many-to-One)
usuario = ForeignKey(User, on_delete=CASCADE)

# Pedido → Produto (Many-to-One)
produto = ForeignKey(Produto, on_delete=PROTECT)
```

**Explicação do `on_delete`:**
- `CASCADE` em User: Se usuário for deletado, seus pedidos também são
- `PROTECT` em Produto: Produto não pode ser deletado se tiver pedidos

---

## Boas Práticas Implementadas

### 1. Segurança
✅ CSRF Protection ativo
✅ Passwords hasheados (PBKDF2)
✅ Validação de permissões (`is_staff`)
✅ `@login_required` em views protegidas
✅ Sessões separadas admin/site

### 2. Validação de Dados
✅ Email único no cadastro
✅ Estoque validado antes da compra
✅ Quantidade mínima (1) nas compras
✅ Limpeza de username (espaços)

### 3. UX/UI
✅ Mensagens de feedback (`messages.success/error`)
✅ Loading states em formulários
✅ Validação visual inline
✅ Placeholder text descritivo
✅ Botões desabilitados durante submit

### 4. Performance
✅ Queries otimizadas (`.filter(estoque__gt=0)`)
✅ Ordenação no banco (`order_by('-data')`)
✅ `get_object_or_404` (evita try/except)

### 5. Código Limpo
✅ Docstrings em views
✅ Comentários explicativos
✅ Nomes descritivos de variáveis
✅ Separação de responsabilidades
✅ DRY (BootstrapFormMixin)

### 6. SEO e Acessibilidade
✅ Tags semânticas (`<header>`, `<main>`, `<footer>`)
✅ Alt text em imagens
✅ Labels associados a inputs
✅ Contraste adequado (WCAG AA)

---

## Ambiente de Desenvolvimento

### Estrutura Recomendada

```bash
# 1. Ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 2. Dependências
pip install django pillow

# 3. Migrações
python manage.py migrate

# 4. Superuser
python manage.py createsuperuser

# 5. Servidor
python manage.py runserver
```

### Variáveis de Ambiente (Produção)

```python
# settings.py
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

---

## Troubleshooting

### Erro: `NoReverseMatch for 'admin_login'`
**Causa:** URL não configurada em `Projeto/urls.py`
**Solução:** Verificar que a rota existe:
```python
path('admin-login/', views.admin_login, name='admin_login'),
```

### Erro: `Pillow is not installed`
**Causa:** Biblioteca de imagens não instalada
**Solução:**
```bash
pip install Pillow
```

### Problema: Sessão admin/site não separa
**Causa:** Middleware não configurado ou em ordem errada
**Solução:** Verificar `settings.py`:
```python
MIDDLEWARE = [
    ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'app.middleware.SeparateAdminAuthMiddleware',  # Após Auth!
    ...
]
```

---

**Última atualização:** Novembro 2025
**Versão:** 1.0
**Desenvolvedor:** Frank Oliveira
