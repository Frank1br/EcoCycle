# EcoCycle - E-commerce Sustentável

![Django](https://img.shields.io/badge/Django-5.2.8-092E20?style=flat&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat&logo=python&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.0-7952B3?style=flat&logo=bootstrap&logoColor=white)

Plataforma de e-commerce para venda de produtos eletrônicos recondicionados, promovendo sustentabilidade e economia circular.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Sistema de Autenticação](#sistema-de-autenticação)
- [Modelos de Dados](#modelos-de-dados)
- [Screenshots](#screenshots)
- [Contribuindo](#contribuindo)

## 🌱 Sobre o Projeto

O **EcoCycle** é uma plataforma web desenvolvida em Django que promove a venda de produtos eletrônicos recondicionados, contribuindo para a redução do lixo eletrônico e promovendo a economia circular. O projeto foi desenvolvido como trabalho acadêmico da disciplina de Desenvolvimento Web 3.

### Objetivos

- Promover sustentabilidade através da venda de produtos recondicionados
- Oferecer uma plataforma intuitiva e moderna para compra de eletrônicos
- Implementar sistema de autenticação seguro e separado para usuários e administradores
- Fornecer interface administrativa completa para gestão de produtos e pedidos

## ✨ Funcionalidades

### Para Usuários
- ✅ Cadastro e login de usuários (com validação de email único)
- ✅ Navegação de produtos disponíveis
- ✅ Sistema de compras com controle de estoque
- ✅ Histórico de pedidos no perfil do usuário
- ✅ Formulário de contato
- ✅ Interface responsiva (mobile-first)

### Para Administradores
- ✅ Login administrativo separado do site
- ✅ Gestão completa de produtos (CRUD)
- ✅ Visualização de pedidos
- ✅ Gestão de conteúdo da página inicial
- ✅ Controle de mensagens de contato

## 🛠️ Tecnologias Utilizadas

### Backend
- **Django 5.2.8** - Framework web Python
- **SQLite** - Banco de dados
- **Pillow** - Processamento de imagens

### Frontend
- **Bootstrap 5.3.0** - Framework CSS
- **Bootstrap Icons 1.11.3** - Biblioteca de ícones
- **Google Fonts (Inter)** - Tipografia
- **CSS3** - Estilização customizada
- **JavaScript** - Interatividade

### Design System
- **Paleta Eco-Tech**:
  - Primary Dark: `#0F172A` (navbar/footer)
  - Primary Green: `#10B981` (ações/sustentabilidade)
  - Background: `#E2E8F0` (fundo das páginas)
  - Text: `#1E293B` (texto principal)

## 🚀 Instalação

### Pré-requisitos

- Python 3.13 ou superior
- pip (gerenciador de pacotes Python)
- Virtualenv (recomendado)

### Passo a Passo

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd p2Web3
```

2. **Crie e ative o ambiente virtual**
```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. **Instale as dependências**
```bash
pip install django pillow
```

4. **Execute as migrações**
```bash
python3 manage.py migrate
```

5. **Crie um superusuário (admin)**
```bash
python3 manage.py createsuperuser
```

6. **Inicie o servidor de desenvolvimento**
```bash
python3 manage.py runserver
```

7. **Acesse a aplicação**
- Site: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- Login Admin Separado: http://127.0.0.1:8000/admin-login/

## ⚙️ Configuração

### Arquivos de Mídia

O projeto está configurado para servir arquivos de mídia em modo de desenvolvimento. Os uploads são salvos em:

```
media/
├── produtos/     # Fotos dos produtos
└── site/         # Logo e imagens da página
```

### Configurações Importantes

**settings.py**
```python
# Redirecionamento após login/logout
LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'index'
LOGIN_URL = 'login'

# Middleware customizado para separação de sessões
MIDDLEWARE = [
    ...
    'app.middleware.SeparateAdminAuthMiddleware',
    ...
]
```

## 📁 Estrutura do Projeto

```
p2Web3/
├── Projeto/                    # Configurações do projeto Django
│   ├── settings.py            # Configurações principais
│   ├── urls.py                # Rotas principais
│   └── wsgi.py                # WSGI para deploy
│
├── app/                       # Aplicação principal
│   ├── migrations/            # Migrações do banco de dados
│   ├── template/              # Templates HTML
│   │   ├── admin/
│   │   │   └── admin_login.html     # Login admin separado
│   │   ├── registration/
│   │   │   ├── login.html           # Login do site
│   │   │   └── cadastro.html        # Cadastro de usuários
│   │   ├── base.html                # Template base
│   │   ├── index.html               # Página inicial
│   │   ├── comprar.html             # Página de compra
│   │   └── perfil.html              # Perfil do usuário
│   │
│   ├── models.py              # Modelos de dados
│   ├── views.py               # Views/Controllers
│   ├── forms.py               # Formulários Django
│   ├── middleware.py          # Middleware customizado
│   ├── admin.py               # Configuração do Django Admin
│   └── urls.py                # URLs do app (não utilizado)
│
├── media/                     # Arquivos de mídia (uploads)
├── db.sqlite3                 # Banco de dados SQLite
├── manage.py                  # CLI do Django
└── README.md                  # Este arquivo
```

## 🔐 Sistema de Autenticação

O projeto implementa um sistema de autenticação **dual** e **separado** para usuários do site e administradores.

### Características

#### Login do Site (`/login/`)
- Qualquer usuário pode fazer login
- Define `session['auth_type'] = 'site'`
- Redireciona para a página inicial
- Possui botão "É admin? Clique aqui" para acesso administrativo

#### Login Admin (`/admin-login/`)
- **Acesso restrito**: Apenas usuários com `is_staff=True`
- Define `session['auth_type'] = 'admin'`
- Redireciona para `/admin/`
- Interface visual diferenciada (tema vermelho/laranja)

### Middleware de Separação

O middleware `SeparateAdminAuthMiddleware` garante a separação de sessões:

```python
# app/middleware.py
class SeparateAdminAuthMiddleware:
    """
    Middleware que mantém sessões separadas entre admin e site.
    - Login no admin ≠ Login no site
    - Login no site ≠ Login no admin
    """
```

**Comportamento:**
- Se usuário está logado como **admin** e tenta acessar o site → logout automático
- Se usuário está logado no **site** e tenta acessar `/admin/` → logout automático

### Views Customizadas

**site_login()** - [app/views.py:43-68](app/views.py#L43-L68)
```python
def site_login(request):
    """Login para usuários do site"""
    # Define auth_type='site' na sessão
```

**admin_login()** - [app/views.py:61-89](app/views.py#L61-L89)
```python
def admin_login(request):
    """Login exclusivo para administradores"""
    # Verifica is_staff e define auth_type='admin'
```

## 📊 Modelos de Dados

### Pagina
Gerencia o conteúdo da página inicial.

```python
class Pagina(models.Model):
    titulo = CharField(max_length=100)
    subtitulo = CharField(max_length=200)
    descricao = TextField()
    logo_do_site = ImageField()
    imagem_sobre = ImageField()
```

### Produto
Representa produtos disponíveis para venda.

```python
class Produto(models.Model):
    nome = CharField(max_length=100)
    descricao = TextField()
    preco = DecimalField(max_digits=10, decimal_places=2)
    estoque = IntegerField()
    foto = ImageField()
    data_adicao = DateTimeField(auto_now_add=True)
```

### Pedido
Registra as compras realizadas.

```python
class Pedido(models.Model):
    usuario = ForeignKey(User)
    produto = ForeignKey(Produto)
    quantidade = IntegerField()
    total = DecimalField(max_digits=10, decimal_places=2)
    data = DateTimeField(auto_now_add=True)
```

### Contato
Armazena mensagens do formulário de contato.

```python
class Contato(models.Model):
    nome = CharField(max_length=100)
    email = EmailField()
    mensagem = TextField()
    data_envio = DateTimeField(auto_now_add=True)
```

## 🎨 Design e Interface

### Princípios de Design
- **Mobile-First**: Interface responsiva priorizando dispositivos móveis
- **Eco-Friendly**: Paleta de cores verde sustentável
- **Moderna**: Gradientes, sombras e animações suaves
- **Acessível**: Contraste adequado e navegação intuitiva

### Componentes Principais

#### Hero Section
Seção de destaque na página inicial com:
- Título e subtítulo
- Botões de ação contextuais (muda conforme autenticação)
- Imagem ilustrativa

#### Product Cards
Cards de produtos com:
- Foto do produto
- Nome, descrição e preço
- Badge de estoque
- Botão de compra
- Hover effects com elevação

#### Forms
Formulários estilizados com:
- Input groups com ícones
- Validação visual
- Mensagens de erro contextuais
- Loading states

## 📱 Responsividade

O projeto é totalmente responsivo com breakpoints:

```css
/* Mobile */
@media (max-width: 576px) { ... }

/* Tablet */
@media (max-width: 768px) { ... }

/* Desktop */
@media (min-width: 992px) { ... }
```

## 🧪 Validações Implementadas

### Cadastro de Usuários
- ✅ Email único (não permite duplicados)
- ✅ Username aceita espaços (para nomes completos)
- ✅ Senha com validadores do Django
- ✅ Confirmação de senha

### Compras
- ✅ Validação de estoque disponível
- ✅ Quantidade mínima (1)
- ✅ Usuário deve estar autenticado
- ✅ Produto deve existir

## 🔒 Segurança

- CSRF Protection ativado
- Passwords hasheados (Django default)
- Sessões separadas para admin e usuários
- Login requerido para rotas protegidas
- Validação de permissões admin

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 👨‍💻 Desenvolvedor

**Frank Oliveira**

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos.

## 🙏 Agradecimentos

- Disciplina de Desenvolvimento Web 3
- Comunidade Django
- Bootstrap Team
- Font Awesome / Bootstrap Icons

---

⭐ Se este projeto foi útil, considere dar uma estrela!
