/**
 * search.js
 * Manejo de la interfaz de búsqueda de declaraciones
 */

(function() {
    'use strict';

    // Configuración de elementos del DOM
    const CONFIG = {
        searchTypes: {
            HASH_ID: 'hash_id',
            AUTHOR: 'author',
            EMAIL: 'email'
        },
        elements: {
            searchTypeInput: 'search_type',
            inputs: {
                hashId: 'input_hash_id',
                author: 'input_author',
                email: 'input_email'
            },
            tabs: {
                hashId: 'tab_hash_id',
                author: 'tab_author',
                email: 'tab_email'
            },
            queries: {
                hash: 'query_hash',
                author: 'query_author',
                email: 'query_email'
            }
        },
        styles: {
            active: ['bg-white', 'text-slate-900', 'shadow-sm'],
            inactive: ['text-slate-600', 'hover:text-slate-900']
        }
    };

    /**
     * Obtiene todos los elementos del DOM necesarios
     */
    function getElements() {
        return {
            searchTypeInput: document.getElementById(CONFIG.elements.searchTypeInput),
            inputs: {
                hashId: document.getElementById(CONFIG.elements.inputs.hashId),
                author: document.getElementById(CONFIG.elements.inputs.author),
                email: document.getElementById(CONFIG.elements.inputs.email)
            },
            tabs: {
                hashId: document.getElementById(CONFIG.elements.tabs.hashId),
                author: document.getElementById(CONFIG.elements.tabs.author),
                email: document.getElementById(CONFIG.elements.tabs.email)
            },
            queries: {
                hash: document.getElementById(CONFIG.elements.queries.hash),
                author: document.getElementById(CONFIG.elements.queries.author),
                email: document.getElementById(CONFIG.elements.queries.email)
            }
        };
    }

    /**
     * Oculta todos los inputs de búsqueda
     */
    function hideAllInputs(elements) {
        Object.values(elements.inputs).forEach(input => {
            if (input) input.classList.add('hidden');
        });
    }

    /**
     * Deshabilita todos los campos de query
     */
    function disableAllQueries(elements) {
        Object.values(elements.queries).forEach(query => {
            if (query) {
                query.disabled = true;
                query.name = '';
            }
        });
    }

    /**
     * Resetea los estilos de todas las tabs
     */
    function resetAllTabStyles(elements) {
        Object.values(elements.tabs).forEach(tab => {
            if (tab) {
                tab.classList.remove(...CONFIG.styles.active);
                tab.classList.add(...CONFIG.styles.inactive);
            }
        });
    }

    /**
     * Activa un input específico
     */
    function activateInput(inputElement, queryElement) {
        if (inputElement) inputElement.classList.remove('hidden');
        if (queryElement) {
            queryElement.disabled = false;
            queryElement.name = 'query';
            queryElement.focus();
        }
    }

    /**
     * Activa una tab específica
     */
    function activateTab(tabElement) {
        if (tabElement) {
            tabElement.classList.add(...CONFIG.styles.active);
            tabElement.classList.remove(...CONFIG.styles.inactive);
        }
    }

    /**
     * Cambia el tipo de búsqueda
     * @param {string} type - Tipo de búsqueda ('hash_id', 'author', 'email')
     */
    function setSearchType(type) {
        const elements = getElements();
        
        if (!elements.searchTypeInput) {
            console.error('No se encontró el input de tipo de búsqueda');
            return;
        }

        // Actualizar el valor del tipo de búsqueda
        elements.searchTypeInput.value = type;

        // Resetear todos los elementos
        hideAllInputs(elements);
        disableAllQueries(elements);
        resetAllTabStyles(elements);

        // Activar el tipo correspondiente
        switch (type) {
            case CONFIG.searchTypes.AUTHOR:
                activateInput(elements.inputs.author, elements.queries.author);
                activateTab(elements.tabs.author);
                break;

            case CONFIG.searchTypes.EMAIL:
                activateInput(elements.inputs.email, elements.queries.email);
                activateTab(elements.tabs.email);
                break;

            case CONFIG.searchTypes.HASH_ID:
            default:
                activateInput(elements.inputs.hashId, elements.queries.hash);
                activateTab(elements.tabs.hashId);
                break;
        }
    }

    /**
     * Inicializa la interfaz de búsqueda
     */
    function initSearch() {
        const elements = getElements();
        
        if (!elements.searchTypeInput) {
            console.warn('Interfaz de búsqueda no encontrada');
            return;
        }

        // Obtener el tipo de búsqueda actual
        const currentType = elements.searchTypeInput.value || CONFIG.searchTypes.HASH_ID;
        
        // Configurar los listeners de los botones de tab
        Object.values(elements.tabs).forEach((tab) => {
            if (tab) {
                tab.addEventListener('click', (e) => {
                    e.preventDefault();
                    const type = tab.getAttribute('data-search-type');
                    if (type) {
                        setSearchType(type);
                    }
                });
            }
        });

        // Inicializar el estado correcto
        if (currentType === CONFIG.searchTypes.AUTHOR || currentType === CONFIG.searchTypes.EMAIL) {
            setSearchType(currentType);
        }
    }

    // Exponer funciones globalmente si es necesario
    window.setSearchType = setSearchType;

    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSearch);
    } else {
        initSearch();
    }

})();
