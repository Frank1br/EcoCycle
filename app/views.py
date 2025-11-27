from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate
from .models import Pagina, Produto, Pedido
from .forms import ContatoForm, CadastroForm, LoginForm

def index(request):
    pagina = Pagina.objects.first()
    produtos = Produto.objects.filter(estoque__gt=0) 
    
    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mensagem enviada com sucesso!')
            return redirect('index')
    else:
        form = ContatoForm()

    context = {'pagina': pagina, 'produtos': produtos, 'form_contato': form}
    return render(request, 'index.html', context)

def cadastro(request):
    # Se o usuário já está autenticado, redireciona para a página inicial
    if request.user.is_authenticated:
        messages.info(request, 'Você já está logado!')
        return redirect('index')

    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Define o tipo de autenticação como 'site'
            request.session['auth_type'] = 'site'
            messages.success(request, f'Bem-vindo, {user.username}! Sua conta foi criada com sucesso.')
            return redirect('index')
    else:
        form = CadastroForm()
    return render(request, 'registration/cadastro.html', {'form': form})

def site_login(request):
    """
    View de login para usuários do site.
    Define o tipo de sessão como 'site' para separar do login admin.
    """
    # Se já está autenticado como site, redireciona para index
    if request.user.is_authenticated and request.session.get('auth_type') == 'site':
        return redirect('index')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                # Define o tipo de autenticação como 'site'
                request.session['auth_type'] = 'site'
                messages.success(request, f'Bem-vindo de volta, {user.username}!')
                return redirect('index')
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})

@login_required
def comprar(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    if request.method == 'POST':
        try:
            qtd = int(request.POST.get('quantidade', 1))
        except ValueError:
            qtd = 1
        
        if qtd > produto.estoque:
            messages.error(request, 'Estoque insuficiente.')
        elif qtd <= 0:
            messages.error(request, 'Quantidade inválida.')
        else:
            Pedido.objects.create(usuario=request.user, produto=produto, quantidade=qtd, total=produto.preco*qtd)
            produto.estoque -= qtd
            produto.save()
            messages.success(request, 'Compra realizada!')
            return redirect('perfil')
    return render(request, 'comprar.html', {'produto': produto})

@login_required
def perfil(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-data')
    return render(request, 'perfil.html', {'pedidos': pedidos})

def admin_login(request):
    """
    View de login exclusiva para administradores.
    Define o tipo de sessão como 'admin' para separar do login do site.
    """
    # Se já está autenticado como admin, redireciona para o admin
    if request.user.is_authenticated and request.session.get('auth_type') == 'admin':
        return redirect('/admin/')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            # Verifica se o usuário é staff (admin)
            if user is not None and user.is_staff:
                login(request, user)
                # Define o tipo de autenticação como 'admin'
                request.session['auth_type'] = 'admin'
                messages.success(request, f'Bem-vindo ao painel administrativo, {user.username}!')
                return redirect('/admin/')
            else:
                messages.error(request, 'Acesso negado. Apenas administradores podem acessar esta área.')
    else:
        form = LoginForm()

    return render(request, 'admin/admin_login.html', {'form': form})
