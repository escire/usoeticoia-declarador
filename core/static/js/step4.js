/**
 * JavaScript para Paso 4: Resultado
 * Tabs, copiar al portapapeles, y feedback visual
 */

// Estado para ORCID y ROR
let orcidState = {
    status: 'idle', // idle, checking, valid, invalid, error
    data: null,
    timeout: null
};

let rorState = {
    status: 'idle',
    results: [],
    selected: null,
    timeout: null,
    showDropdown: false
};

// ==================== ORCID Functions ====================

function validateORCIDFormat(orcid) {
    const pattern = /^\d{4}-\d{4}-\d{4}-\d{3}[0-9X]$/;
    return pattern.test(orcid);
}

function formatORCID(value) {
    const clean = value.replace(/[^0-9X]/gi, '').toUpperCase().slice(0, 16);
    const parts = [];
    for (let i = 0; i < clean.length; i += 4) {
        parts.push(clean.slice(i, i + 4));
    }
    return parts.join('-');
}

async function fetchOrcidProfile(orcid) {
    try {
        const response = await fetch(`https://pub.orcid.org/v3.0/${orcid}`, {
            headers: { 'Accept': 'application/json' }
        });

        if (!response.ok) throw new Error('ORCID no encontrado');

        const data = await response.json();
        const person = data.person || {};
        const name = person.name || {};
        const givenNames = name['given-names']?.value || '';
        const familyName = name['family-name']?.value || '';
        const fullName = `${givenNames} ${familyName}`.trim();

        return {
            name: fullName,
            isNamePublic: !!fullName,
            orcid: orcid,
            profileUrl: `https://orcid.org/${orcid}`
        };
    } catch (error) {
        throw new Error('No se pudo verificar el ORCID');
    }
}

async function validateORCIDReal(orcid) {
    orcidState.status = 'checking';
    updateOrcidFeedback();

    try {
        const profile = await fetchOrcidProfile(orcid);
        orcidState.data = profile;
        orcidState.status = 'valid';
        updateOrcidFeedback();
    } catch (error) {
        orcidState.status = 'error';
        orcidState.data = {
            name: '', isNamePublic: false, orcid, profileUrl: '',
            error: error.message || 'Error desconocido'
        };
        updateOrcidFeedback();
    }
}

function updateOrcidFeedback() {
    const indicator = document.getElementById('orcidIndicator');
    const feedback = document.getElementById('orcidFeedback');
    const input = document.getElementById('author_orcid');

    if (!indicator || !feedback || !input) return;

    // Update indicator
    if (orcidState.status === 'checking') {
        indicator.innerHTML = '⏳';
    } else if (orcidState.status === 'valid') {
        indicator.innerHTML = '✓';
        input.classList.add('border-emerald-400', 'bg-emerald-50/30');
        input.classList.remove('border-rose-300');
    } else if (orcidState.status === 'invalid' || orcidState.status === 'error') {
        indicator.innerHTML = '⚠️';
        input.classList.remove('border-emerald-400', 'bg-emerald-50/30');
    } else {
        indicator.innerHTML = '';
        input.classList.remove('border-emerald-400', 'bg-emerald-50/30', 'border-rose-300');
    }

    // Update feedback message
    if (orcidState.status === 'valid' && orcidState.data) {
        feedback.innerHTML = `
            <div class="p-3 bg-emerald-50 rounded-lg border border-emerald-100 text-sm text-emerald-800">
                <p class="font-medium">✓ Identidad verificada</p>
                ${orcidState.data.name ? `<p class="text-emerald-600/80 text-xs mt-0.5">Registrado como: ${orcidState.data.name}</p>` : ''}
            </div>
        `;
    } else {
        feedback.innerHTML = '';
    }
}

function handleOrcidInput(e) {
    const input = e.target;
    let value = formatORCID(input.value);
    input.value = value;

    clearTimeout(orcidState.timeout);

    if (value.length === 19) {
        orcidState.timeout = setTimeout(() => {
            if (validateORCIDFormat(value)) {
                validateORCIDReal(value);
            } else {
                orcidState.status = 'invalid';
                orcidState.data = { name: '', isNamePublic: false, orcid: value, profileUrl: '', error: 'Formato inválido' };
                updateOrcidFeedback();
            }
        }, 600);
    } else {
        orcidState.status = 'idle';
        orcidState.data = null;
        updateOrcidFeedback();
    }
}

// ==================== ROR Functions ====================

async function searchRorOrganizations(query) {
    if (!query || query.length < 3) {
        rorState.results = [];
        rorState.showDropdown = false;
        updateRorDropdown();
        return;
    }

    try {
        rorState.status = 'searching';
        const encodedQuery = encodeURIComponent(query);
        const response = await fetch(`https://api.ror.org/v2/organizations?query=${encodedQuery}`);

        if (!response.ok) throw new Error('Error en búsqueda');

        const data = await response.json();
        rorState.results = (data.items || []).slice(0, 8).map(org => {
            const displayName = org.names?.find(n => n.types?.includes('ror_display'))?.value ||
                              org.names?.find(n => n.types?.includes('label'))?.value ||
                              org.names?.[0]?.value || 'Sin nombre';

            const country = org.locations?.[0]?.geonames_details?.country_name || '';
            const rorId = org.id || '';

            return {
                id: rorId,
                name: displayName,
                country: country,
                types: org.types || [],
                url: rorId
            };
        });

        rorState.status = 'idle';
        rorState.showDropdown = rorState.results.length > 0;
        updateRorDropdown();
    } catch (error) {
        rorState.status = 'error';
        rorState.results = [];
        rorState.showDropdown = false;
        updateRorDropdown();
    }
}

function updateRorDropdown() {
    const dropdown = document.getElementById('rorDropdown');
    if (!dropdown) return;

    if (!rorState.showDropdown || rorState.results.length === 0) {
        dropdown.classList.add('hidden');
        return;
    }

    dropdown.classList.remove('hidden');
    dropdown.innerHTML = rorState.results.map((org, idx) => `
        <div class="ror-result px-4 py-3 hover:bg-slate-50 cursor-pointer border-b border-slate-100 last:border-0 transition-colors"
             data-index="${idx}">
            <div class="flex items-start gap-3">
                <div class="flex-shrink-0 mt-1">
                    <svg class="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                    </svg>
                </div>
                <div class="flex-1 min-w-0">
                    <p class="text-sm font-semibold text-slate-900 truncate">${org.name}</p>
                    <p class="text-xs text-slate-500 mt-0.5">${org.country || 'País desconocido'}</p>
                </div>
            </div>
        </div>
    `).join('');

    // Agregar event listeners
    dropdown.querySelectorAll('.ror-result').forEach((el) => {
        el.addEventListener('click', () => {
            const idx = parseInt(el.dataset.index);
            selectRorOrganization(rorState.results[idx]);
        });
    });
}

function selectRorOrganization(org) {
    rorState.selected = org;
    rorState.showDropdown = false;

    // Actualizar input y campo oculto
    const input = document.getElementById('author_affiliation');
    const hiddenInput = document.getElementById('author_affiliation_ror_id');
    if (input) input.value = org.name;
    if (hiddenInput) hiddenInput.value = org.id;

    updateRorDropdown();
    updateRorFeedback();
}

function updateRorFeedback() {
    const feedback = document.getElementById('rorFeedback');
    if (!feedback) return;

    if (rorState.selected) {
        feedback.innerHTML = `
            <div class="p-3 bg-emerald-50 rounded-lg border border-emerald-100 text-sm">
                <div class="flex items-start gap-2">
                    <svg class="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <div class="flex-1">
                        <p class="font-medium text-emerald-800">Institución verificada en ROR</p>
                        <a href="${rorState.selected.url}" target="_blank" rel="noopener noreferrer"
                           class="text-xs text-emerald-600 hover:text-emerald-700 underline mt-1 inline-flex items-center gap-1">
                            Ver en ROR
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                            </svg>
                        </a>
                    </div>
                </div>
            </div>
        `;
    } else {
        feedback.innerHTML = '';
    }
}

function handleAffiliationInput(e) {
    const value = e.target.value;

    // Clear ROR selection if user types something different
    if (rorState.selected && value !== rorState.selected.name) {
        rorState.selected = null;
        document.getElementById('author_affiliation_ror_id').value = '';
        updateRorFeedback();
    }

    clearTimeout(rorState.timeout);
    if (value.length >= 3) {
        rorState.timeout = setTimeout(() => {
            searchRorOrganizations(value);
        }, 400);
    } else {
        rorState.results = [];
        rorState.showDropdown = false;
        updateRorDropdown();
    }
}

// Close ROR dropdown when clicking outside
document.addEventListener('click', function(e) {
    const dropdown = document.getElementById('rorDropdown');
    const input = document.getElementById('author_affiliation');
    if (dropdown && input && !dropdown.contains(e.target) && e.target !== input) {
        rorState.showDropdown = false;
        updateRorDropdown();
    }
});

document.addEventListener('DOMContentLoaded', function() {
    let currentTab = 'text';

    // Setup ORCID input listener
    const orcidInput = document.getElementById('author_orcid');
    if (orcidInput) {
        orcidInput.addEventListener('input', handleOrcidInput);
    }

    // Setup Affiliation/ROR input listener
    const affiliationInput = document.getElementById('author_affiliation');
    if (affiliationInput) {
        affiliationInput.addEventListener('input', handleAffiliationInput);
        affiliationInput.addEventListener('focus', function() {
            if (rorState.results.length > 0) {
                rorState.showDropdown = true;
                updateRorDropdown();
            }
        });
    }

    window.showTab = function(tab) {
        currentTab = tab;
        const textContent = document.getElementById('contentText');
        const jsonContent = document.getElementById('contentJson');
        const textBtn = document.getElementById('tabText');
        const jsonBtn = document.getElementById('tabJson');

        if (tab === 'text') {
            textContent.classList.remove('hidden');
            jsonContent.classList.add('hidden');
            textBtn.classList.add('text-primary-700', 'bg-white', 'border-b-2', 'border-primary-500');
            textBtn.classList.remove('text-slate-500');
            jsonBtn.classList.remove('text-primary-700', 'bg-white', 'border-b-2', 'border-primary-500');
            jsonBtn.classList.add('text-slate-500');
        } else {
            jsonContent.classList.remove('hidden');
            textContent.classList.add('hidden');
            jsonBtn.classList.add('text-primary-700', 'bg-white', 'border-b-2', 'border-primary-500');
            jsonBtn.classList.remove('text-slate-500');
            textBtn.classList.remove('text-primary-700', 'bg-white', 'border-b-2', 'border-primary-500');
            textBtn.classList.add('text-slate-500');
        }
    };

    window.copyContent = function() {
        const content = currentTab === 'text'
            ? document.getElementById('contentText').innerText
            : document.getElementById('contentJson').innerText;

        navigator.clipboard.writeText(content).then(() => {
            const copyIcon = document.getElementById('copyIcon');
            const copyText = document.getElementById('copyText');
            const copyBtn = document.getElementById('copyBtn');

            // Feedback visual
            copyIcon.innerText = '✓';
            copyText.innerText = 'Copiado';
            copyBtn.classList.add('bg-emerald-50', 'text-emerald-700', 'border-emerald-200');

            setTimeout(() => {
                copyIcon.innerText = '📋';
                copyText.innerText = 'Copiar';
                copyBtn.classList.remove('bg-emerald-50', 'text-emerald-700', 'border-emerald-200');
            }, 2000);
        }).catch(err => {
            console.error('Error al copiar:', err);
            alert('No se pudo copiar al portapapeles');
        });
    };

    // Abrir modal para capturar datos
    window.openSaveModal = function() {
        const modal = document.getElementById('saveModal');
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden'; // Prevenir scroll
    };

    // Cerrar modal
    window.closeSaveModal = function() {
        const modal = document.getElementById('saveModal');
        modal.classList.add('hidden');
        document.body.style.overflow = 'auto'; // Restaurar scroll
    };

    // Manejar envío del formulario
    document.getElementById('saveForm')?.addEventListener('submit', async function(e) {
        e.preventDefault();

        const modalSaveBtn = document.getElementById('modalSaveBtn');
        const modalSaveBtnText = document.getElementById('modalSaveBtnText');
        const modalErrorMessage = document.getElementById('modalErrorMessage');
        const authorName = document.getElementById('author_name').value.trim();
        const authorEmail = document.getElementById('author_email').value.trim();

        // Validar campos
        if (!authorName || !authorEmail) {
            modalErrorMessage.querySelector('p').innerText = 'Por favor completa todos los campos';
            modalErrorMessage.classList.remove('hidden');
            return;
        }

        // Deshabilitar botón mientras se procesa
        modalSaveBtn.disabled = true;
        modalSaveBtnText.innerText = 'Guardando...';
        modalSaveBtn.classList.add('opacity-75', 'cursor-not-allowed');
        modalErrorMessage.classList.add('hidden');

        try {
            // Obtener el idioma actual de la URL
            const currentPath = window.location.pathname;
            const langMatch = currentPath.match(/^\/(es|en|pt|it)\//);
            const langPrefix = langMatch ? langMatch[0] : '/';

            // Intentar obtener el CSRF token de múltiples fuentes
            const csrfToken = window.CSRF_TOKEN || getCookie('csrftoken') || document.querySelector('[name=csrfmiddlewaretoken]')?.value;

            // Obtener campos opcionales ORCID y ROR
            const authorOrcid = document.getElementById('author_orcid')?.value.trim() || '';
            const authorAffiliationRorId = document.getElementById('author_affiliation_ror_id')?.value.trim() || '';
            const authorOrcidVerified = orcidState.status === 'valid';

            const response = await fetch(langPrefix + 'api/guardar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    author_name: authorName,
                    author_email: authorEmail,
                    author_orcid: authorOrcid,
                    author_orcid_verified: authorOrcidVerified,
                    author_affiliation_ror_id: authorAffiliationRorId
                })
            });

            // Verificar si la respuesta es exitosa
            if (!response.ok) {
                const text = await response.text();
                console.error('Response error:', text);
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.success) {
                // Cerrar modal
                closeSaveModal();

                // Mostrar mensaje de éxito brevemente
                const saveMessage = document.getElementById('saveMessage');
                saveMessage.querySelector('p').innerText = '✓ ' + data.message + ' - Redirigiendo...';
                saveMessage.classList.remove('hidden');
                saveMessage.classList.add('border-emerald-300', 'bg-emerald-50');

                // Redirigir a la vista de la declaración
                const saveSection = document.getElementById('saveDeclarationSection');
                if (saveSection) {
                    saveSection.style.transition = 'opacity 0.5s';
                    saveSection.style.opacity = '0';
                }

                // Redirigir después de un breve delay
                setTimeout(() => {
                    if (data.redirect_url) {
                        window.location.href = data.redirect_url;
                    } else {
                        // Fallback: construir URL manualmente
                        window.location.href = langPrefix + 'declaracion/' + data.declaration_id + '/';
                    }
                }, 800);
            } else {
                throw new Error(data.error || 'Error al guardar');
            }
        } catch (error) {
            console.error('Error:', error);
            modalErrorMessage.querySelector('p').innerText = '✗ Error al guardar: ' + error.message;
            modalErrorMessage.classList.remove('hidden');

            // Rehabilitar botón
            modalSaveBtn.disabled = false;
            modalSaveBtnText.innerText = 'Reintentar';
            modalSaveBtn.classList.remove('opacity-75', 'cursor-not-allowed');
        }
    });

    // Saltar el guardado y solo descargar
    window.skipSave = function() {
        const saveSection = document.getElementById('saveDeclarationSection');
        if (saveSection) {
            saveSection.style.transition = 'all 0.3s';
            saveSection.style.opacity = '0';
            saveSection.style.maxHeight = saveSection.offsetHeight + 'px';

            setTimeout(() => {
                saveSection.style.maxHeight = '0';
                saveSection.style.padding = '0';
                saveSection.style.margin = '0';
                saveSection.style.overflow = 'hidden';

                // Crear mensaje pequeño para cambiar de opinión
                setTimeout(() => {
                    const changeMindText = saveSection.getAttribute('data-change-mind-text') || '¿Cambiaste de opinión? Haz clic aquí para guardar la declaración';
                    const changeMindbtn = document.createElement('div');
                    changeMindbtn.id = 'changeMindBtn';
                    changeMindbtn.className = 'text-center py-2';
                    changeMindbtn.innerHTML = `
                        <button onclick="showSaveSection()" class="text-sm text-emerald-600 hover:text-emerald-700 underline">
                            ${changeMindText}
                        </button>
                    `;
                    saveSection.parentNode.insertBefore(changeMindbtn, saveSection.nextSibling);
                }, 300);
            }, 300);
        }
    };

    // Mostrar nuevamente la sección de guardado si cambia de opinión
    window.showSaveSection = function() {
        const saveSection = document.getElementById('saveDeclarationSection');
        const changeMindBtn = document.getElementById('changeMindBtn');

        if (saveSection) {
            // Remover el botón de cambiar de opinión
            if (changeMindBtn) {
                changeMindBtn.remove();
            }

            // Restaurar la sección
            saveSection.style.maxHeight = 'none';
            saveSection.style.padding = '';
            saveSection.style.margin = '';
            saveSection.style.overflow = '';
            saveSection.style.opacity = '1';
        }
    };

    // Función helper para obtener el CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Animar la aparición de los badges
    const badges = document.querySelectorAll('.bg-slate-800, .bg-white.border');
    badges.forEach((badge, index) => {
        setTimeout(() => {
            badge.classList.add('animate-in', 'fade-in', 'slide-in-from-bottom-2');
        }, index * 100);
    });
});
