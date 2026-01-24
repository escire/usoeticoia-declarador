/**
 * view_declaration.js
 * Manejo de la interfaz de visualización de declaraciones
 */

(function() {
    'use strict';

    // Configuración
    const CONFIG = {
        elements: {
            tabs: {
                text: 'tab-text',
                json: 'tab-json'
            },
            contents: {
                text: 'content-text',
                json: 'content-json'
            },
            outputs: {
                text: 'text-output',
                json: 'json-output'
            },
            url: {
                input: 'permanentUrl',
                button: 'copyUrlBtn'
            }
        },
        styles: {
            tabActive: ['border-primary-600', 'text-primary-600', 'bg-white'],
            tabInactive: ['border-transparent', 'text-slate-600'],
            buttonCopied: ['bg-emerald-100', 'text-emerald-700'],
            buttonDefault: ['bg-slate-100', 'hover:bg-slate-200', 'text-slate-700'],
            urlButtonCopied: ['bg-emerald-600'],
            urlButtonDefault: ['bg-primary-600', 'hover:bg-primary-700']
        },
        timeouts: {
            copyFeedback: 2000
        },
        selectors: {
            tabContent: '.tab-content',
            tabButton: '.tab-button'
        }
    };

    /**
     * Cambia entre las pestañas de visualización
     * @param {string} tabName - Nombre de la pestaña ('text' o 'json')
     */
    function showTab(tabName) {
        // Ocultar todos los contenidos de tabs
        const allContents = document.querySelectorAll(CONFIG.selectors.tabContent);
        allContents.forEach(content => {
            content.classList.add('hidden');
        });

        // Remover estado activo de todas las tabs
        const allButtons = document.querySelectorAll(CONFIG.selectors.tabButton);
        allButtons.forEach(button => {
            button.classList.remove(...CONFIG.styles.tabActive);
            button.classList.add(...CONFIG.styles.tabInactive);
        });

        // Mostrar el contenido de la tab seleccionada
        const selectedContent = document.getElementById(`content-${tabName}`);
        if (selectedContent) {
            selectedContent.classList.remove('hidden');
        }

        // Activar la tab seleccionada
        const activeTab = document.getElementById(`tab-${tabName}`);
        if (activeTab) {
            activeTab.classList.remove(...CONFIG.styles.tabInactive);
            activeTab.classList.add(...CONFIG.styles.tabActive);
        }
    }

    /**
     * Copia la URL permanente al portapapeles
     */
    function copyUrl() {
        const urlInput = document.getElementById(CONFIG.elements.url.input);
        const button = document.getElementById(CONFIG.elements.url.button);

        if (!urlInput || !button) {
            console.error('Elementos de URL no encontrados');
            return;
        }

        navigator.clipboard.writeText(urlInput.value)
            .then(() => {
                showCopyFeedback(button, CONFIG.styles.urlButtonCopied, CONFIG.styles.urlButtonDefault);
            })
            .catch(err => {
                console.error('Error al copiar URL:', err);
                alert('No se pudo copiar la URL. Por favor, cópiala manualmente.');
            });
    }

    /**
     * Copia el contenido de un elemento al portapapeles
     * @param {string} elementId - ID del elemento cuyo contenido se copiará
     * @param {Event} event - Evento del click
     */
    function copyToClipboard(elementId, event) {
        const element = document.getElementById(elementId);
        const button = event ? event.target.closest('button') : null;

        if (!element) {
            console.error(`Elemento con ID "${elementId}" no encontrado`);
            return;
        }

        if (!button) {
            console.error('Botón no encontrado');
            return;
        }

        const text = element.textContent;

        navigator.clipboard.writeText(text)
            .then(() => {
                showCopyFeedback(button, CONFIG.styles.buttonCopied, CONFIG.styles.buttonDefault);
            })
            .catch(err => {
                console.error('Error al copiar contenido:', err);
                alert('No se pudo copiar el contenido. Por favor, cópialo manualmente.');
            });
    }

    /**
     * Muestra feedback visual cuando se copia contenido
     * @param {HTMLElement} button - El botón que se clickeó
     * @param {Array} copiedStyles - Clases CSS para el estado copiado
     * @param {Array} defaultStyles - Clases CSS para el estado por defecto
     */
    function showCopyFeedback(button, copiedStyles, defaultStyles) {
        if (!button) return;

        const originalHTML = button.innerHTML;

        // Cambiar a estado "copiado"
        button.innerHTML = `
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            <span>${getTranslation('copied')}</span>
        `;
        
        button.classList.remove(...defaultStyles);
        button.classList.add(...copiedStyles);

        // Restaurar estado original después del timeout
        setTimeout(() => {
            button.innerHTML = originalHTML;
            button.classList.remove(...copiedStyles);
            button.classList.add(...defaultStyles);
        }, CONFIG.timeouts.copyFeedback);
    }

    /**
     * Obtiene la traducción para una clave
     * @param {string} key - Clave de traducción
     * @returns {string} Texto traducido
     */
    function getTranslation(key) {
        const translations = {
            'copied': 'Copiado' // Se puede extender para soporte multiidioma
        };
        return translations[key] || key;
    }

    /**
     * Configura los event listeners para las tabs
     */
    function setupTabListeners() {
        const tabs = document.querySelectorAll(CONFIG.selectors.tabButton);
        
        tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                const tabName = tab.getAttribute('data-tab-name');
                if (tabName) {
                    showTab(tabName);
                }
            });
        });
    }

    /**
     * Configura el listener para copiar URL
     */
    function setupUrlCopyListener() {
        const button = document.getElementById(CONFIG.elements.url.button);
        if (button) {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                copyUrl();
            });
        }
    }

    /**
     * Configura los listeners para copiar contenido
     */
    function setupContentCopyListeners() {
        // Buscar todos los botones con data-copy-target
        const copyButtons = document.querySelectorAll('[data-copy-target]');
        
        copyButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = button.getAttribute('data-copy-target');
                if (targetId) {
                    copyToClipboard(targetId, e);
                }
            });
        });
    }

    /**
     * Inicializa la interfaz
     */
    function init() {
        // Mostrar la pestaña de texto por defecto
        showTab('text');

        // Configurar event listeners
        setupTabListeners();
        setupUrlCopyListener();
        setupContentCopyListeners();
    }

    // Exponer funciones globalmente para compatibilidad con onclick inline (temporal)
    window.showTab = showTab;
    window.copyUrl = copyUrl;
    window.copyToClipboard = copyToClipboard;

    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
