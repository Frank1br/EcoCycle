from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.contrib.auth import views as auth_views

# Importamos apenas as views, que é o padrão seguro
from app import views

# Definimos o formulário de login DIRETAMENTE na view personalizada se precisarmos,
# ou usamos um truque para não importar o forms.py aqui.
# Mas a melhor forma é mover a lógica do 'authentication_form' para dentro do views.py
# ou usar a view padrão e deixar o template cuidar do resto.

# Vamos usar a view de login padrão, mas apontando para o template correto.
# O formulário personalizado (com placeholders) já deve ser usado automaticamente
# se configurarmos corretamente ou se passarmos na view.

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rotas do App
    path('', views.index, name='index'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('comprar/<int:produto_id>/', views.comprar, name='comprar'),
    path('perfil/', views.perfil, name='perfil'),
    
    # Login: Usando a view que criaremos no app/views.py para evitar circular import
    path('login/', views.site_login, name='login'),
    path('admin-login/', views.admin_login, name='admin_login'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Rota para média em produção
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)