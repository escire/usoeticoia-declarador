"""
Vistas para descargar declaraciones en diferentes formatos.
"""
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils.translation import get_language
from datetime import datetime
import random
import string

from ..models import Declaration
from ..utils import (
    generate_declaration_text,
    generate_declaration_json,
    compute_hash
)
from .declarations import get_session_data


def _get_declaration_for_download(request):
    """Obtiene la Declaration guardada en DB desde la sesión actual."""
    declaration_id = request.session.get('generated_declaration', {}).get('declaration_id')
    if declaration_id:
        try:
            return Declaration.objects.get(declaration_id=declaration_id)
        except Declaration.DoesNotExist:
            pass
    return None


@require_http_methods(["GET"])
def download_text(request):
    """Download declaration as text file"""
    current_lang = get_language()

    declaration = _get_declaration_for_download(request)
    if not declaration:
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        return HttpResponseRedirect(reverse('step1'))

    hash_value = declaration.validation_hash
    text_output = generate_declaration_text(declaration, hash_value, current_lang)

    response = HttpResponse(text_output, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="declaracion-ia-v4.txt"'
    return response


@require_http_methods(["GET"])
def download_json(request):
    """Download declaration as JSON file"""
    current_lang = get_language()

    declaration = _get_declaration_for_download(request)
    if not declaration:
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        return HttpResponseRedirect(reverse('step1'))

    hash_value = declaration.validation_hash
    json_output = generate_declaration_json(declaration, hash_value, current_lang)

    response = HttpResponse(json_output, content_type='application/json; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="declaracion-ia-v4.json"'
    return response
