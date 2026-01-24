"""
Vistas para búsqueda y verificación de declaraciones.
"""
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.utils.translation import get_language
from django.db.models import Q
import re

from ..models import Declaration
from ..utils import (
    generate_declaration_text,
    generate_declaration_json,
)
from ..translations import get_translated_glossary


def sanitize_query(query, search_type='hash_id'):
    """
    Sanitiza y valida la entrada de búsqueda según el tipo.
    
    """
    if not query:
        return '', False
    
    # Eliminar espacios en blanco excesivos
    query = query.strip()
    
    if search_type == 'hash_id':
        # Solo permitir caracteres alfanuméricos
        sanitized = re.sub(r'[^A-Za-z0-9]', '', query)
        # Hash: 16 caracteres, ID: 8 caracteres
        is_valid = len(sanitized) in [8, 16]
        return sanitized.upper(), is_valid
    
    elif search_type == 'email':
        # Validación básica de email (permisiva para soportar emails incompletos)
        # Permite: usuario@dominio o usuario@dominio.ext
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,})?$'
        is_valid = bool(re.match(email_pattern, query)) and '@' in query
        # Convertir a minúsculas para búsqueda consistente
        return query.lower(), is_valid
    
    elif search_type == 'author':
        # Permitir letras, espacios, guiones, apóstrofes, acentos
        sanitized = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\'\-\.]', '', query)
        sanitized = ' '.join(sanitized.split())  # Normalizar espacios
        is_valid = len(sanitized) >= 2  # Al menos 2 caracteres
        return sanitized, is_valid
    
    return query, True


@require_http_methods(["GET"])
def search_declaration(request):
    """Página de búsqueda de declaraciones por hash, ID, autor o email"""
    current_lang = get_language()

    context = {
        'glossary': get_translated_glossary(current_lang),
        'result': None,
        'results': [],  # For multiple results (author/email search)
        'not_found': False,
        'query': '',
        'search_type': 'hash_id',  # 'hash_id', 'author', or 'email'
        'error_message': ''
    }

    # Usar GET en lugar de POST para preservar parámetros al cambiar idioma
    query = request.GET.get('query', '').strip()
    search_type = request.GET.get('search_type', 'hash_id')
    
    if query:
        query = query
        search_type = search_type
    context['query'] = query
    context['search_type'] = search_type

    if query:
        # Sanitizar la consulta
        sanitized_query, is_valid = sanitize_query(query, search_type)
        
        if not is_valid:
            context['error_message'] = 'invalid_query'
            context['not_found'] = True
        else:
            try:
                if search_type == 'author':
                    # Búsqueda por nombre de autor (case-insensitive, partial match)
                    declarations = Declaration.objects.filter(
                        author_name__icontains=sanitized_query
                    ).order_by('-created_at')[:20]  # Limitar a 20 resultados

                    if declarations.exists():
                        context['results'] = list(declarations)
                    else:
                        context['not_found'] = True
                
                elif search_type == 'email':
                    # Búsqueda por email (case-insensitive, flexible)
                    # 1. Búsqueda exacta
                    declarations = Declaration.objects.filter(
                        author_email__iexact=sanitized_query
                    ).order_by('-created_at')[:20]
                    
                    # 2. Si no encuentra, buscar emails que empiecen con la query
                    if not declarations.exists():
                        declarations = Declaration.objects.filter(
                            author_email__istartswith=sanitized_query
                        ).order_by('-created_at')[:20]
                    
                    # 3. Si aún no encuentra, intentar sin el dominio
                    if not declarations.exists() and '@' in sanitized_query:
                        # Extraer solo la parte antes del @
                        email_parts = sanitized_query.split('@')
                        username = email_parts[0]
                        domain_start = email_parts[1].split('.')[0] if len(email_parts) > 1 else ''
                        
                        # Buscar por usuario@dominio_parcial
                        if domain_start:
                            partial_email = f"{username}@{domain_start}"
                            declarations = Declaration.objects.filter(
                                author_email__istartswith=partial_email
                            ).order_by('-created_at')[:20]

                    if declarations.exists():
                        context['results'] = list(declarations)
                    else:
                        context['not_found'] = True
                
                else:  # hash_id
                    # Búsqueda por hash o ID (exact match)
                    # Primero intentar con hash
                    declaration = Declaration.objects.filter(
                        validation_hash__iexact=sanitized_query
                    ).first()

                    # Si no se encuentra, intentar con ID
                    if not declaration:
                        declaration = Declaration.objects.filter(
                            declaration_id__iexact=sanitized_query
                        ).first()

                    if declaration:
                        context['result'] = declaration
                        context['text_output'] = generate_declaration_text(
                            declaration, 
                            declaration.validation_hash, 
                            current_lang
                        )
                        context['json_output'] = generate_declaration_json(
                            declaration, 
                            declaration.validation_hash, 
                            current_lang
                        )
                    else:
                        context['not_found'] = True
                        
            except Exception as e:
                # Log error en producción
                print(f"Error en búsqueda: {e}")
                context['not_found'] = True
                context['error_message'] = 'search_error'

    return render(request, 'core/search.html', context)


@require_http_methods(["GET"])
def view_declaration(request, declaration_id):
    """Ver una declaración específica por su ID"""
    current_lang = get_language()

    try:
        declaration = Declaration.objects.get(declaration_id=declaration_id)

        text_output = generate_declaration_text(declaration, declaration.validation_hash, current_lang)
        json_output = generate_declaration_json(declaration, declaration.validation_hash, current_lang)

        context = {
            'declaration': declaration,
            'text_output': text_output,
            'json_output': json_output,
            'hash': declaration.validation_hash,
            'glossary': get_translated_glossary(current_lang),
        }
        return render(request, 'core/view_declaration.html', context)
    except Declaration.DoesNotExist:
        return render(request, 'core/not_found.html', {'query': declaration_id})
