"""
Context processors para templates
"""
from django.conf import settings


def recaptcha_keys(request):
    """
    Agrega las keys de reCAPTCHA al contexto de los templates
    """
    return {
        'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY,
        'RECAPTCHA_ENABLED': settings.RECAPTCHA_ENABLED,
    }


def site_settings(request):
    """
    Provee configuraciones del sitio al contexto de los templates.
    Permite usar URLs absolutas consistentes en toda la aplicación.
    """
    # Determinar el dominio base
    if settings.SITE_DOMAIN:
        # Usar el dominio configurado en .env (producción)
        base_url = settings.SITE_DOMAIN.rstrip('/')
    else:
        # Fallback al dominio actual del request (desarrollo)
        base_url = f"{request.scheme}://{request.get_host()}"
    
    return {
        'SITE_DOMAIN': settings.SITE_DOMAIN,
        'BASE_URL': base_url,
    }
