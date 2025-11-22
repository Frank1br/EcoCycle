from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from app import views
from django.contrib.auth import views as auth_views

# IMPORTANTE: Importamos o LoginForm personalizado para conectar com a view de login
from app.forms import LoginForm 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rotas principais do App
    path('', views.index, name='index'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('comprar/<int:produto_id>/', views.comprar, name='comprar'),
    path('perfil/', views.perfil, name='perfil'),
    
    # Rota de Login
    # Aqui conectamos o template 'login.html' com o formulário 'LoginForm'
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        authentication_form=LoginForm
    ), name='login'),

    # Rota de Logout
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

# Configuração para servir arquivos de mídia (imagens) em ambiente de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)