from .models import Pagina

def dados_do_site(request):
    """
    Disponibiliza as configurações da página (logo, nome, etc.)
    para todos os templates do sistema.
    """
    # Pega a primeira configuração encontrada no banco ou None se não existir
    pagina = Pagina.objects.first()
    
    # Retorna um dicionário que será mesclado ao contexto dos templates
    return {'site_config': pagina}