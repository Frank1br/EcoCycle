from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from .models import Pagina, Produto, Pedido
from .forms import ContatoForm, CadastroForm

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
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = CadastroForm()
    return render(request, 'registration/cadastro.html', {'form': form})

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
