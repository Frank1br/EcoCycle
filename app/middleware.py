"""
Middleware para separar autenticação de admin e usuários do site
"""
from django.contrib.auth import logout
from django.urls import resolve


class SeparateAdminAuthMiddleware:
    """
    Middleware que mantém sessões separadas entre admin e site.

    - Se o usuário fizer login no admin, não estará logado no site
    - Se o usuário fizer login no site, não estará logado no admin
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Identifica se a requisição é para área admin ou site
        url_name = resolve(request.path_info).url_name
        url_namespace = resolve(request.path_info).namespace

        is_admin_area = (
            request.path.startswith('/admin/') or
            url_name == 'admin_login' or
            url_namespace == 'admin'
        )

        # Marca no request se estamos na área admin
        request.is_admin_area = is_admin_area

        # Verifica se há conflito de sessão
        if request.user.is_authenticated:
            session_type = request.session.get('auth_type', 'site')

            # Se usuário logado como 'site' tenta acessar admin (ou vice-versa)
            if is_admin_area and session_type == 'site':
                # Faz logout automático para evitar conflito
                logout(request)
            elif not is_admin_area and session_type == 'admin':
                # Faz logout automático para evitar conflito
                logout(request)

        response = self.get_response(request)
        return response
