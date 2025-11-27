# ============================================================================
# ATENÇÃO: Este arquivo NÃO está sendo usado!
# O arquivo de configuração de URLs principal é: Projeto/urls.py
# Este arquivo existe apenas para referência.
# ============================================================================

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from app import views
from django.contrib.auth import views as auth_views 

urlpatterns = [
    path('admin/', admin.site.urls),

    # Rotas principais do App
    path('', views.index, name='index'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('comprar/<int:produto_id>/', views.comprar, name='comprar'),
    path('perfil/', views.perfil, name='perfil'),

    # Rota de Login do Site
    path('login/', views.site_login, name='login'),

    # Rota de Login do Admin (separada)
    path('admin-login/', views.admin_login, name='admin_login'),

    # Rota de Logout
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

# Configuração para servir arquivos de mídia (imagens) em ambiente de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)