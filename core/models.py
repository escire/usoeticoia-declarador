from django.db import models
import json
import hashlib
from datetime import datetime

class Signer(models.Model):
    """Modelo para almacenar firmantes del compromiso de uso ético de IA"""

    # Identificadores únicos
    signer_id = models.CharField(max_length=20, unique=True, editable=False)
    validation_hash = models.CharField(max_length=64, unique=True, editable=False)
    hash_short = models.CharField(max_length=8, editable=False)

    # Información personal
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    orcid = models.CharField(max_length=19)  # Formato: 0000-0000-0000-0000
    country = models.CharField(max_length=100, blank=True, null=True)

    # Información profesional
    affiliation = models.CharField(max_length=300)
    affiliation_ror_id = models.CharField(max_length=200, blank=True, null=True)  # ROR ID
    discipline = models.CharField(max_length=100)
    profile_url = models.URLField(blank=True, null=True)
    declaration = models.TextField(blank=True, null=True, max_length=280)

    # Verificación ORCID
    orcid_verified = models.BooleanField(default=False)
    orcid_registered_name = models.CharField(max_length=200, blank=True, null=True)

    # Consentimientos
    agreed_to_terms = models.BooleanField(default=True)
    public_listing = models.BooleanField(default=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Firmante'
        verbose_name_plural = 'Firmantes'

    def save(self, *args, **kwargs):
        if not self.signer_id:
            import random
            import string
            self.signer_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        if not self.validation_hash:
            # Generar hash basado en datos del firmante
            hash_input = f"{self.full_name}{self.email}{self.orcid}{self.affiliation}{self.created_at or datetime.now()}"
            self.validation_hash = hashlib.sha256(hash_input.encode()).hexdigest()
            self.hash_short = self.validation_hash[:8]

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} - {self.affiliation}"

    def get_verification_url(self, request=None):
        """Retorna la URL pública de verificación"""
        from django.urls import reverse
        from django.conf import settings

        # Construir la URL relativa
        relative_url = reverse('signer_verify', kwargs={'hash_short': self.hash_short})

        if request:
            # Usar el dominio actual del request
            return request.build_absolute_uri(relative_url)
        elif settings.SITE_DOMAIN:
            # Usar el dominio configurado en settings
            return f"{settings.SITE_DOMAIN.rstrip('/')}{relative_url}"
        else:
            # Fallback: solo la URL relativa
            return relative_url

    @property
    def country_flag(self):
        """Retorna el emoji de bandera correspondiente al país"""
        COUNTRY_FLAGS = {
            'Alemania': '🇩🇪',
            'Argentina': '🇦🇷',
            'Bélgica': '🇧🇪',
            'Bolivia': '🇧🇴',
            'Brasil': '🇧🇷',
            'Chile': '🇨🇱',
            'Colombia': '🇨🇴',
            'Costa Rica': '🇨🇷',
            'Cuba': '🇨🇺',
            'Ecuador': '🇪🇨',
            'El Salvador': '🇸🇻',
            'España': '🇪🇸',
            'Francia': '🇫🇷',
            'Guatemala': '🇬🇹',
            'Honduras': '🇭🇳',
            'Italia': '🇮🇹',
            'México': '🇲🇽',
            'Nicaragua': '🇳🇮',
            'Panamá': '🇵🇦',
            'Paraguay': '🇵🇾',
            'Perú': '🇵🇪',
            'Polonia': '🇵🇱',
            'Portugal': '🇵🇹',
            'Puerto Rico': '🇵🇷',
            'Reino Unido': '🇬🇧',
            'República Dominicana': '🇩🇴',
            'Suiza': '🇨🇭',
            'Uruguay': '🇺🇾',
            'Venezuela': '🇻🇪',
            'Otro': '🌍'
        }
        return COUNTRY_FLAGS.get(self.country, '🌍') if self.country else '🌍'


class Declaration(models.Model):
    """Model to store AI transparency declarations"""

    # Unique identifiers
    declaration_id = models.CharField(max_length=20, unique=True, editable=False)
    validation_hash = models.CharField(max_length=64, blank=True)

    # Author information (required when saving)
    author_name = models.CharField(max_length=200, blank=True)
    author_email = models.EmailField(blank=True)
    author_orcid = models.CharField(max_length=19, blank=True)  # Formato: 0000-0000-0000-0000
    author_orcid_verified = models.BooleanField(default=False)
    author_affiliation_ror_id = models.CharField(max_length=200, blank=True)  # ROR ID

    # Declaration type: True if AI was used, False if no AI was used
    ai_used = models.BooleanField(default=True)

    # Diagnostic/Traceability
    selected_checklist_ids = models.JSONField(default=list, blank=True)

    # Usage Type
    usage_types = models.JSONField(default=list)
    custom_usage_type = models.TextField(blank=True)

    # AI Tool Information
    ai_tool_name = models.CharField(max_length=200)
    ai_tool_version = models.CharField(max_length=100, blank=True)
    ai_tool_provider = models.CharField(max_length=200, blank=True)
    ai_tool_date_month = models.IntegerField()
    ai_tool_date_year = models.IntegerField()

    # Purpose and Prompts
    specific_purpose = models.TextField()
    prompts = models.JSONField(default=list)

    # Content Integration
    content_use_modes = models.JSONField(default=list, blank=True)
    custom_content_use_mode = models.TextField(blank=True)
    content_use_context = models.TextField(blank=True)

    # Human Review
    human_review_level = models.IntegerField(default=0)
    reviewer_name = models.CharField(max_length=200, blank=True)
    reviewer_role = models.CharField(max_length=200, blank=True)

    # License
    license = models.CharField(max_length=50, default='None')

    # Draft status
    is_draft = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.declaration_id:
            import random
            import string
            self.declaration_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        super().save(*args, **kwargs)

    def compute_hash(self, content):
        """Compute SHA-256 hash of declaration content"""
        return hashlib.sha256(content.encode()).hexdigest()[:16].upper()

    def __str__(self):
        return f"Declaration {self.declaration_id} - {self.ai_tool_name}"
