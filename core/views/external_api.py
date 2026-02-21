"""
API externa para integración con sistemas de terceros.
Autenticación mediante API keys (Authorization: Bearer <key>).
"""
import json
from datetime import datetime, timezone
from functools import wraps

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.conf import settings

import re

from ..models import Declaration, APIKey
from ..utils import generate_declaration_text, generate_declaration_json, compute_hash


def _normalize_orcid(raw: str) -> str:
    """Extrae el ID ORCID en formato 0000-0000-0000-0000, aceptando URL o ID directo."""
    if not raw:
        return ''
    match = re.search(r'\d{4}-\d{4}-\d{4}-\d{3}[\dX]', raw, re.IGNORECASE)
    return match.group(0) if match else raw.strip()


def require_api_key(view_func):
    """Decorator que valida la API key del header Authorization: Bearer <key>"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse(
                {'success': False, 'error': 'API key requerida. Usa el header: Authorization: Bearer <api_key>'},
                status=401
            )

        raw_key = auth_header[len('Bearer '):].strip()
        try:
            api_key = APIKey.objects.get(key=raw_key, is_active=True)
        except APIKey.DoesNotExist:
            return JsonResponse(
                {'success': False, 'error': 'API key inválida o inactiva'},
                status=401
            )

        # Actualizar estadísticas de uso
        APIKey.objects.filter(pk=api_key.pk).update(
            last_used_at=datetime.now(tz=timezone.utc),
            request_count=api_key.request_count + 1
        )

        request.api_key = api_key
        return view_func(request, *args, **kwargs)
    return wrapper


@csrf_exempt
@require_http_methods(["POST"])
@require_api_key
def create_declaration(request):
    """
    Crea una declaración de transparencia IA y la guarda en la base de datos.

    Autenticación: Authorization: Bearer <api_key>
    Content-Type: application/json

    Campos requeridos (ai_used=true):
      - ai_used: true
      - usage_types: lista de tipos (draft, coauthor, writing-support, ideation,
                     analysis, coding, translation, review, other)
      - ai_tool.name: nombre de la herramienta
      - ai_tool.date_month: mes de uso (1-12)
      - ai_tool.date_year: año de uso
      - specific_purpose: descripción del propósito
      - prompts: lista de {id, description}
      - human_review.level: nivel de revisión (0-6)

    Campos requeridos (ai_used=false):
      - ai_used: false

    Campos opcionales en ambos casos:
      - language: "es" | "en" | "pt" | "it" (default: "es")
      - author_name, author_email, author_orcid, author_affiliation_ror_id
      - license: valor de CC_LICENSES

    Respuesta exitosa (200):
      {
        "success": true,
        "declaration_id": "AB12CD34",
        "validation_hash": "ABCDEF0123456789",
        "declaration_url": "https://declarador.io/declaracion/AB12CD34/",
        "text": "...",
        "json_content": {...}
      }
    """
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse(
            {'success': False, 'error': 'El cuerpo de la petición debe ser JSON válido'},
            status=400
        )

    lang = body.get('language', 'es')
    if lang not in ('es', 'en', 'pt', 'it'):
        lang = 'es'

    ai_used = body.get('ai_used', True)

    now = datetime.now(tz=timezone.utc)

    if not ai_used:
        # Declaración sin IA — campos mínimos
        declaration = Declaration(
            ai_used=False,
            author_name=body.get('author_name', '').strip(),
            author_email=body.get('author_email', '').strip(),
            author_orcid=_normalize_orcid(body.get('author_orcid', '')),
            author_affiliation_ror_id=body.get('author_affiliation_ror_id', '').strip(),
            # Campos requeridos por el modelo pero irrelevantes para NO AI
            usage_types=[],
            ai_tool_name='',
            ai_tool_date_month=now.month,
            ai_tool_date_year=now.year,
            specific_purpose='',
            prompts=[],
            human_review_level=0,
        )
    else:
        # Declaración con IA — validar campos requeridos
        errors = []

        usage_types = body.get('usage_types', [])
        if not usage_types:
            errors.append('usage_types es requerido y no puede estar vacío')

        ai_tool = body.get('ai_tool', {})
        if not ai_tool.get('name', '').strip():
            errors.append('ai_tool.name es requerido')

        date_month = ai_tool.get('date_month')
        date_year = ai_tool.get('date_year')
        if not date_month or not isinstance(date_month, int) or not (1 <= date_month <= 12):
            errors.append('ai_tool.date_month debe ser un entero entre 1 y 12')
        if not date_year or not isinstance(date_year, int):
            errors.append('ai_tool.date_year debe ser un entero (ej. 2026)')

        specific_purpose = body.get('specific_purpose', '').strip()
        if not specific_purpose:
            errors.append('specific_purpose es requerido')

        prompts = body.get('prompts', [])
        if not prompts or not any(p.get('description', '').strip() for p in prompts):
            errors.append('prompts debe contener al menos un elemento con description')

        human_review = body.get('human_review', {})
        review_level = human_review.get('level', 0)
        if not isinstance(review_level, int) or not (0 <= review_level <= 6):
            errors.append('human_review.level debe ser un entero entre 0 y 6')

        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        declaration = Declaration(
            ai_used=True,
            selected_checklist_ids=body.get('selected_checklist_ids', []),
            usage_types=usage_types,
            custom_usage_type=body.get('custom_usage_type', '').strip(),
            ai_tool_name=ai_tool.get('name', '').strip(),
            ai_tool_version=ai_tool.get('version', '').strip(),
            ai_tool_provider=ai_tool.get('provider', '').strip(),
            ai_tool_date_month=date_month,
            ai_tool_date_year=date_year,
            specific_purpose=specific_purpose,
            prompts=prompts,
            content_use_modes=body.get('content_use_modes', []),
            custom_content_use_mode=body.get('custom_content_use_mode', '').strip(),
            content_use_context=body.get('content_use_context', '').strip(),
            human_review_level=review_level,
            reviewer_name=human_review.get('reviewer_name', '').strip(),
            reviewer_role=human_review.get('reviewer_role', '').strip(),
            license=body.get('license', 'None'),
            author_name=body.get('author_name', '').strip(),
            author_email=body.get('author_email', '').strip(),
            author_orcid=_normalize_orcid(body.get('author_orcid', '')),
            author_orcid_verified=body.get('author_orcid_verified', False),
            author_affiliation_ror_id=body.get('author_affiliation_ror_id', '').strip(),
        )

    # Calcular hash desde texto sin ID ni hash (el ID se asigna en save())
    declaration_text_no_hash = generate_declaration_text(declaration, None, lang)
    hash_value = compute_hash(declaration_text_no_hash)

    # Guardar primero para que se asigne declaration_id automáticamente
    declaration.validation_hash = hash_value
    declaration.save()

    # Regenerar texto y JSON con declaration_id y hash ya disponibles
    declaration_text = generate_declaration_text(declaration, hash_value, lang)
    declaration_json_str = generate_declaration_json(declaration, hash_value, lang)
    declaration_json = json.loads(declaration_json_str)

    return JsonResponse(_declaration_response(declaration, hash_value, declaration_text, declaration_json, request))


# ---------------------------------------------------------------------------
# Helper compartido
# ---------------------------------------------------------------------------

def _declaration_response(declaration, hash_value, text, json_content, request):
    """Construye el dict de respuesta estándar para una declaración."""
    relative_url = reverse('view_declaration', kwargs={'declaration_id': declaration.declaration_id})
    if hasattr(settings, 'SITE_DOMAIN') and settings.SITE_DOMAIN:
        declaration_url = f"{settings.SITE_DOMAIN.rstrip('/')}{relative_url}"
    else:
        declaration_url = request.build_absolute_uri(relative_url)

    return {
        'success': True,
        'declaration_id': declaration.declaration_id,
        'validation_hash': hash_value,
        'declaration_url': declaration_url,
        'text': text,
        'json_content': json_content,
    }


# ---------------------------------------------------------------------------
# GET /api/v1/declaracion/<identifier>/
# ---------------------------------------------------------------------------

@csrf_exempt
@require_api_key
def get_declaration(request, identifier):
    """
    Recupera una declaración existente por su ID o hash de validación.

    GET /api/v1/declaracion/<identifier>/?lang=es

    <identifier> puede ser:
      - El declaration_id de 8 caracteres  (ej. AB12CD34)
      - El validation_hash de 16 caracteres (ej. ABCDEF0123456789)

    Parámetros query:
      - lang: "es" | "en" | "pt" | "it"  (default: "es")
        Controla el idioma del texto y JSON generados.

    Respuesta exitosa (200):
      {
        "success": true,
        "declaration_id": "AB12CD34",
        "validation_hash": "ABCDEF0123456789",
        "declaration_url": "https://declarador.io/declaracion/AB12CD34/",
        "text": "...",
        "json_content": {...}
      }

    Errores:
      404 — declaración no encontrada
    """
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

    lang = request.GET.get('lang', 'es')
    if lang not in ('es', 'en', 'pt', 'it'):
        lang = 'es'

    identifier = identifier.strip().upper()

    # Buscar por declaration_id (8 chars) o validation_hash (16 chars)
    try:
        if len(identifier) == 8:
            declaration = Declaration.objects.get(declaration_id__iexact=identifier)
        elif len(identifier) == 16:
            declaration = Declaration.objects.get(validation_hash__iexact=identifier)
        else:
            return JsonResponse(
                {'success': False, 'error': 'El identificador debe tener 8 caracteres (ID) o 16 caracteres (hash)'},
                status=400
            )
    except Declaration.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Declaración no encontrada'}, status=404)

    hash_value = declaration.validation_hash
    declaration_text = generate_declaration_text(declaration, hash_value, lang)
    declaration_json_str = generate_declaration_json(declaration, hash_value, lang)
    declaration_json = json.loads(declaration_json_str)

    return JsonResponse(_declaration_response(declaration, hash_value, declaration_text, declaration_json, request))
