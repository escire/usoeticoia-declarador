from django.contrib import admin
from .models import Declaration, Signer, APIKey


@admin.register(Declaration)
class DeclarationAdmin(admin.ModelAdmin):
    list_display = ('declaration_id', 'ai_tool_name', 'created_at', 'is_draft')
    list_filter = ('is_draft', 'created_at', 'license')
    search_fields = ('declaration_id', 'ai_tool_name', 'specific_purpose')
    readonly_fields = ('declaration_id', 'validation_hash', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner_email', 'is_active', 'request_count', 'last_used_at', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'owner_email')
    readonly_fields = ('key', 'created_at', 'last_used_at', 'request_count')

    fieldsets = (
        ('Identificación', {
            'fields': ('name', 'owner_email', 'is_active')
        }),
        ('Credencial', {
            'fields': ('key',),
            'description': 'La API key se genera automáticamente al crear el registro. '
                           'Compártela con el sistema externo para que la use en el header: '
                           'Authorization: Bearer <key>'
        }),
        ('Estadísticas', {
            'fields': ('request_count', 'last_used_at', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Signer)
class SignerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'affiliation', 'discipline', 'orcid_verified', 'created_at')
    list_filter = ('discipline', 'orcid_verified', 'public_listing', 'created_at', 'country')
    search_fields = ('full_name', 'email', 'orcid', 'affiliation')
    readonly_fields = ('signer_id', 'validation_hash', 'hash_short', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Identificación', {
            'fields': ('signer_id', 'validation_hash', 'hash_short')
        }),
        ('Información Personal', {
            'fields': ('full_name', 'email', 'orcid', 'country')
        }),
        ('Información Profesional', {
            'fields': ('affiliation', 'affiliation_ror_id', 'discipline', 'profile_url', 'declaration')
        }),
        ('Verificación ORCID', {
            'fields': ('orcid_verified', 'orcid_registered_name')
        }),
        ('Consentimientos', {
            'fields': ('agreed_to_terms', 'public_listing')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
