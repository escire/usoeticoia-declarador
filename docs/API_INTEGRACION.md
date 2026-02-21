# Integración vía API — Declarador

Guía para sistemas externos que quieran crear declaraciones de transparencia IA directamente, sin pasar por el wizard web.

**Endpoint base:** [https://declarador.usoeticoia.org](https://declarador.usoeticoia.org/)  
**Versión:** v1
**Autenticación:** API Key por header

---

## Índice

1. [Obtener una API Key](#1-obtener-una-api-key)
2. [Autenticación](#2-autenticación)
3. [Crear una declaración](#3-crear-una-declaración-post)
4. [Recuperar una declaración existente](#4-recuperar-una-declaración-existente-get)
5. [Referencia de campos](#5-referencia-de-campos) — [5.1 Comunes](#51-campos-comunes-todos-los-casos) · [5.2 Con IA](#52-campos-para-declaraciones-con-ia-ai_used-true) · [5.3 usage_types](#53-valores-válidos-para-usage_types) · [5.4 content_use_modes](#54-valores-válidos-para-content_use_modes) · [5.5 human_review.level](#55-niveles-de-revisión-humana-human_reviewlevel) · [5.6 license](#56-valores-válidos-para-license) · [5.7 selected_checklist_ids](#57-valores-válidos-para-selected_checklist_ids)
6. [Ejemplos completos](#6-ejemplos-completos)
7. [Errores y códigos de respuesta](#7-errores-y-códigos-de-respuesta)

---

## 1. Obtener una API Key

Contacta al administrador de **declarador.usoeticoia.org** para solicitar una API Key para tu sistema. Se te asignará una clave de 64 caracteres que identifica tu integración.

La key tiene este aspecto:

```
a3f8c1d2e4b7f9a0c2d5e8f1b4a7c0d3e6f9b2a5d8e1f4a7b0c3d6e9f2a5d8
```

---

## 2. Autenticación

Todas las peticiones deben incluir el header:

```http
Authorization: Bearer <tu_api_key>
Content-Type: application/json
```

Si el header falta o la key es inválida/inactiva, recibirás `401 Unauthorized`.

---

## 3. Crear una declaración `POST`

```
POST /api/v1/declaracion/
```

Crea una declaración, la guarda en la base de datos y devuelve el ID, hash de validación, URL pública y el contenido completo en texto y JSON.

### Headers requeridos


| Header          | Valor              |
| --------------- | ------------------ |
| `Authorization` | `Bearer <api_key>` |
| `Content-Type`  | `application/json` |


### Respuesta exitosa `200 OK`

```json
{
  "success": true,
  "declaration_id": "AB12CD34",
  "validation_hash": "ABCDEF0123456789",
  "declaration_url": "https://declarador.usoeticoia.org/declaracion/AB12CD34/",
  "text": "DECLARACIÓN DE TRANSPARENCIA EN EL USO DE IA...",
  "json_content": { ... }
}
```


| Campo             | Descripción                                                 |
| ----------------- | ----------------------------------------------------------- |
| `declaration_id`  | ID único de 8 caracteres                                    |
| `validation_hash` | Hash SHA-256 (16 chars) para verificar integridad           |
| `declaration_url` | URL pública permanente de la declaración                    |
| `text`            | Texto plano de la declaración (para mostrar o adjuntar)     |
| `json_content`    | Declaración estructurada en JSON (para procesar o archivar) |


---

## 4. Recuperar una declaración existente `GET`

```
GET /api/v1/declaracion/<identifier>/?lang=es
```

Devuelve una declaración ya guardada en la base de datos. El identificador puede ser el **ID de 8 caracteres** o el **hash de validación de 16 caracteres**.

### Headers requeridos


| Header          | Valor              |
| --------------- | ------------------ |
| `Authorization` | `Bearer <api_key>` |


### Parámetro de ruta


| Parámetro    | Descripción                                               |
| ------------ | --------------------------------------------------------- |
| `identifier` | `declaration_id` (8 chars) o `validation_hash` (16 chars) |


### Parámetro query opcional


| Parámetro | Valores             | Default | Descripción                                               |
| --------- | ------------------- | ------- | --------------------------------------------------------- |
| `lang`    | `es` `en` `pt` `it` | `es`    | Idioma en que se genera el texto y JSON de la declaración |


### Respuesta exitosa `200 OK`

Misma estructura que el POST:

```json
{
  "success": true,
  "declaration_id": "AB12CD34",
  "validation_hash": "ABCDEF0123456789",
  "declaration_url": "https://declarador.usoeticoia.org/declaracion/AB12CD34/",
  "text": "DECLARACIÓN DE TRANSPARENCIA...",
  "json_content": { ... }
}
```

### Ejemplos rápidos

```bash
# Por declaration_id
curl -H "Authorization: Bearer <api_key>" \
  https://declarador.usoeticoia.org/api/v1/declaracion/AB12CD34/

# Por validation_hash
curl -H "Authorization: Bearer <api_key>" \
  https://declarador.usoeticoia.org/api/v1/declaracion/ABCDEF0123456789/

# En inglés
curl -H "Authorization: Bearer <api_key>" \
  "https://declarador.usoeticoia.org/api/v1/declaracion/AB12CD34/?lang=en"
```

---

## 5. Referencia de campos

### 5.1 Campos comunes (todos los casos)


| Campo                       | Tipo    | Requerido | Descripción                                                                                                                                           |
| --------------------------- | ------- | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ai_used`                   | boolean | Sí        | `true` si se usó IA, `false` si no se usó                                                                                                             |
| `language`                  | string  | No        | Idioma de la declaración: `"es"` `"en"` `"pt"` `"it"` (default: `"es"`)                                                                               |
| `author_name`               | string  | No        | Nombre del autor                                                                                                                                      |
| `author_email`              | string  | No        | Email del autor                                                                                                                                       |
| `author_orcid`              | string  | No        | ORCID del autor. Acepta formato corto (`0000-0000-0000-0000`) o URL completa (`https://orcid.org/0000-0000-0000-0000`). Se normaliza automáticamente. |
| `author_orcid_verified`     | boolean | No        | Si el ORCID fue verificado (default: `false`)                                                                                                         |
| `author_affiliation_ror_id` | string  | No        | ROR ID de la institución (p.ej. `https://ror.org/02f00yp70`)                                                                                          |


---

### 5.2 Campos para declaraciones con IA (`ai_used: true`)


| Campo                        | Tipo    | Requerido   | Descripción                                                 |
| ---------------------------- | ------- | ----------- | ----------------------------------------------------------- |
| `usage_types`                | array   | **Sí**      | Tipos de uso de IA (ver tabla abajo)                        |
| `custom_usage_type`          | string  | Condicional | Descripción si `"other"` está en `usage_types`              |
| `ai_tool`                    | object  | **Sí**      | Información de la herramienta                               |
| `ai_tool.name`               | string  | **Sí**      | Nombre de la herramienta (p.ej. `"ChatGPT"`)                |
| `ai_tool.version`            | string  | No          | Versión (p.ej. `"4o"`, `"3.5-turbo"`)                       |
| `ai_tool.provider`           | string  | No          | Proveedor (p.ej. `"OpenAI"`, `"Anthropic"`)                 |
| `ai_tool.date_month`         | integer | **Sí**      | Mes de uso (1–12)                                           |
| `ai_tool.date_year`          | integer | **Sí**      | Año de uso (p.ej. `2026`)                                   |
| `specific_purpose`           | string  | **Sí**      | Descripción del propósito específico del uso                |
| `prompts`                    | array   | **Sí**      | Lista de prompts usados (al menos uno con texto)            |
| `prompts[].id`               | string  | Sí          | Identificador del prompt (p.ej. `"1"`, `"2"`)               |
| `prompts[].description`      | string  | Sí          | Texto del prompt                                            |
| `content_use_modes`          | array   | No          | Modos de integración del contenido (ver tabla abajo)        |
| `custom_content_use_mode`    | string  | Condicional | Descripción si `"Otro"` está en `content_use_modes`         |
| `content_use_context`        | string  | No          | Contexto adicional sobre la integración del contenido       |
| `human_review`               | object  | No          | Información de revisión humana                              |
| `human_review.level`         | integer | No          | Nivel de revisión 0–6 (default: `0`)                        |
| `human_review.reviewer_name` | string  | No          | Nombre del revisor (si level > 0)                           |
| `human_review.reviewer_role` | string  | No          | Rol del revisor (p.ej. `"Director de tesis"`)               |
| `selected_checklist_ids`     | array   | No          | IDs de preguntas diagnósticas respondidas (ver sección 5.7) |
| `license`                    | string  | No          | Licencia del trabajo (ver tabla abajo)                      |


---

### 5.3 Valores válidos para `usage_types`


| Valor               | Descripción                                                          |
| ------------------- | -------------------------------------------------------------------- |
| `"draft"`           | Generación de borrador — La IA escribió una primera versión completa |
| `"coauthor"`        | Co-creación sustantiva — Colaboración iterativa IA-humano            |
| `"writing-support"` | Asistencia de estilo — Mejora de forma sin alterar el fondo          |
| `"ideation"`        | Ideación y estructura — Brainstorming, esquemas, outlines            |
| `"analysis"`        | Análisis de datos — Resumen, extracción, síntesis de información     |
| `"coding"`          | Generación de código — Scripts, algoritmos, debugging                |
| `"translation"`     | Traducción técnica — Textos académicos entre idiomas                 |
| `"review"`          | Simulación de revisión — La IA como revisor par simulado             |
| `"other"`           | Otro uso no listado (requiere `custom_usage_type`)                   |


Se pueden combinar varios: `["draft", "writing-support"]`

---

### 5.4 Valores válidos para `content_use_modes`


| Valor (exacto)                             | Descripción                                    |
| ------------------------------------------ | ---------------------------------------------- |
| `"Incorporado tal cual (Verbatim)"`        | Texto de la IA sin modificar                   |
| `"Editado parcialmente (ajustes menores)"` | Ajustes menores sobre el texto de la IA        |
| `"Reescrito sustancialmente"`              | El contenido fue profundamente modificado      |
| `"Usado solo como inspiración/referencia"` | Solo se tomaron ideas, no texto                |
| `"Sintetizado con otras fuentes"`          | Combinado con otras fuentes humanas            |
| `"Otro"`                                   | Otro modo (requiere `custom_content_use_mode`) |


---

### 5.5 Niveles de revisión humana (`human_review.level`)


| Nivel | Etiqueta                 | Descripción                                                                       |
| ----- | ------------------------ | --------------------------------------------------------------------------------- |
| `0`   | Sin revisión             | Contenido usado directamente sin verificación **(RIESGO ALTO)**                   |
| `1`   | Revisión superficial     | Lectura rápida de coherencia general                                              |
| `2`   | Revisión gramatical      | Corrección de errores, sin verificar hechos                                       |
| `3`   | Verificación selectiva   | Spot-checking de datos clave o afirmaciones dudosas                               |
| `4`   | Contrastación documental | Verificación de citas y datos contra fuentes primarias                            |
| `5`   | Validación experta       | Revisión profunda por experto en la materia                                       |
| `6`   | Revisión crítica y ética | Análisis exhaustivo de sesgos, originalidad, ética y precisión técnica **(GOLD)** |


---

### 5.6 Valores válidos para `license`


| Valor               | Descripción                                            |
| ------------------- | ------------------------------------------------------ |
| `"None"`            | Sin licencia especificada (default)                    |
| `"CC BY 4.0"`       | Creative Commons Atribución                            |
| `"CC BY-SA 4.0"`    | Creative Commons Atribución-CompartirIgual             |
| `"CC BY-NC 4.0"`    | Creative Commons Atribución-NoComercial                |
| `"CC BY-NC-SA 4.0"` | Creative Commons Atribución-NoComercial-CompartirIgual |
| `"CC BY-ND 4.0"`    | Creative Commons Atribución-SinDerivadas               |
| `"CC BY-NC-ND 4.0"` | Creative Commons Atribución-NoComercial-SinDerivadas   |
| `"CC0"`             | Dominio público                                        |
| `"Copyright"`       | Todos los derechos reservados                          |


---

### 5.7 Valores válidos para `selected_checklist_ids`

Campo opcional. Representa las preguntas diagnósticas que el sistema respondió afirmativamente para detectar el tipo de uso de IA. Si se omite, la declaración muestra "Selección manual directa", indicando que los `usage_types` fueron elegidos directamente.


| ID     | Pregunta diagnóstica                                            | `usage_type` sugerido |
| ------ | --------------------------------------------------------------- | --------------------- |
| `"q1"` | ¿Generó texto nuevo (párrafos, capítulos) que usaste como base? | `draft`               |
| `"q2"` | ¿Te ayudó a escribir código, scripts o fórmulas matemáticas?    | `coding`              |
| `"q3"` | ¿Resumió artículos, extrajo datos o analizó documentos PDF?     | `analysis`            |
| `"q4"` | ¿Tradujo textos técnicos o abstracts a otro idioma?             | `translation`         |
| `"q5"` | ¿Sugirió estructuras, preguntas de investigación o ideas?       | `ideation`            |
| `"q6"` | ¿Solo mejoró la redacción, el vocabulario o la ortografía?      | `writing-support`     |
| `"q7"` | ¿Evaluó tu trabajo buscando errores o debilidades?              | `review`              |


**Ejemplo:** `"selected_checklist_ids": ["q1", "q6"]`

Los IDs son independientes de los `usage_types` — puedes enviar ambos con distintos valores si tu sistema tiene su propia lógica de detección.

---

## 6. Ejemplos completos

### Ejemplo 1: Declaración con IA (caso típico)

```bash
curl -X POST https://declarador.usoeticoia.org/api/v1/declaracion/ \
  -H "Authorization: Bearer a3f8c1d2e4b7f9a0c2d5e8f1b4a7c0d3e6f9b2a5d8e1f4a7b0c3d6e9f2a5d8" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "es",
    "ai_used": true,
    "usage_types": ["draft", "writing-support"],
    "ai_tool": {
      "name": "ChatGPT",
      "version": "4o",
      "provider": "OpenAI",
      "date_month": 2,
      "date_year": 2026
    },
    "specific_purpose": "Redacción del apartado teórico del TFG sobre cambio climático",
    "prompts": [
      {"id": "1", "description": "Escribe una introducción académica sobre el impacto del cambio climático en los ecosistemas mediterráneos"},
      {"id": "2", "description": "Mejora el estilo y la coherencia del siguiente párrafo manteniendo el significado original"}
    ],
    "content_use_modes": ["Editado parcialmente (ajustes menores)"],
    "human_review": {
      "level": 4,
      "reviewer_name": "Dr. Ana López",
      "reviewer_role": "Directora de TFG"
    },
    "license": "CC BY 4.0",
    "author_name": "María García Sánchez",
    "author_email": "maria.garcia@universidad.edu",
    "author_orcid": "0000-0002-1825-0097"
  }'
```

**Respuesta:**

```json
{
  "success": true,
  "declaration_id": "K7M2P9XQ",
  "validation_hash": "3A8F1C2D5E9B4A7F",
  "declaration_url": "https://declarador.usoeticoia.org/declaracion/K7M2P9XQ/",
  "text": "DECLARACIÓN DE TRANSPARENCIA EN EL USO DE IA EN TRABAJO ACADÉMICO\n═════...",
  "json_content": {
    "declarationType": "academic-ai-transparency",
    "schemaVersion": "1.0.0",
    "id": "K7M2P9XQ",
    "validationHash": "3A8F1C2D5E9B4A7F",
    "author": {
      "name": "María García Sánchez",
      "email": "maria.garcia@universidad.edu",
      "orcid": "0000-0002-1825-0097"
    },
    "usage": {
      "types": ["draft", "writing-support"],
      "labels": ["Generación de Borrador", "Asistencia de Estilo y Redacción"]
    },
    "tool": {
      "name": "ChatGPT",
      "version": "4o",
      "provider": "OpenAI",
      "date": "2026-02"
    },
    "humanReview": {
      "level": 4,
      "label": "Nivel 4: Contrastación Documental",
      "reviewerName": "Dr. Ana López",
      "reviewerRole": "Directora de TFG"
    }
  }
}
```

---

### Ejemplo 2: Declaración SIN uso de IA

```bash
curl -X POST https://declarador.usoeticoia.org/api/v1/declaracion/ \
  -H "Authorization: Bearer <tu_api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "es",
    "ai_used": false,
    "author_name": "Carlos Ruiz Martín",
    "author_email": "carlos.ruiz@universidad.edu"
  }'
```

**Respuesta:**

```json
{
  "success": true,
  "declaration_id": "N3Q8R1TZ",
  "validation_hash": "F2A5B8C1D4E7F0A3",
  "declaration_url": "https://declarador.usoeticoia.org/declaracion/N3Q8R1TZ/",
  "text": "DECLARACIÓN DE NO USO DE IA EN TRABAJO ACADÉMICO\n═════...",
  "json_content": {
    "declarationType": "academic-no-ai-declaration",
    "id": "N3Q8R1TZ",
    "validationHash": "F2A5B8C1D4E7F0A3",
    "aiUsed": false,
    "statement": "Declaro que no he utilizado herramientas de inteligencia artificial generativa..."
  }
}
```

---

### Ejemplo 3: Con múltiples tipos de uso y diagnóstico

```bash
curl -X POST https://declarador.usoeticoia.org/api/v1/declaracion/ \
  -H "Authorization: Bearer <tu_api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "en",
    "ai_used": true,
    "selected_checklist_ids": ["q1", "q3", "q5"],
    "usage_types": ["coding", "analysis"],
    "ai_tool": {
      "name": "Claude",
      "version": "Sonnet 4.5",
      "provider": "Anthropic",
      "date_month": 1,
      "date_year": 2026
    },
    "specific_purpose": "Statistical analysis and Python scripts for survey data processing",
    "prompts": [
      {"id": "1", "description": "Write a Python script to clean and normalize survey responses from a CSV file"},
      {"id": "2", "description": "Analyze the correlation between variables X and Y and suggest visualizations"}
    ],
    "content_use_modes": ["Reescrito sustancialmente", "Incorporado tal cual (Verbatim)"],
    "content_use_context": "Code was reviewed and adapted; analysis output was included verbatim in appendix",
    "human_review": {"level": 5, "reviewer_role": "Thesis committee"},
    "license": "CC BY-SA 4.0",
    "author_name": "John Smith",
    "author_email": "j.smith@university.edu",
    "author_affiliation_ror_id": "https://ror.org/02f00yp70"
  }'
```

---

### Ejemplo en Python

```python
import requests

API_KEY = "tu_api_key_aqui"
BASE_URL = "https://declarador.usoeticoia.org"

def crear_declaracion(datos: dict) -> dict:
    response = requests.post(
        f"{BASE_URL}/api/v1/declaracion/",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json=datos,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


resultado = crear_declaracion({
    "language": "es",
    "ai_used": True,
    "usage_types": ["draft"],
    "ai_tool": {
        "name": "ChatGPT",
        "version": "4o",
        "provider": "OpenAI",
        "date_month": 2,
        "date_year": 2026,
    },
    "specific_purpose": "Redacción inicial del abstract del artículo",
    "prompts": [
        {"id": "1", "description": "Escribe un abstract de 200 palabras para un artículo sobre..."}
    ],
    "human_review": {"level": 3},
    "author_name": "Pedro Alonso",
    "author_email": "pedro@universidad.edu",
})

print("ID:", resultado["declaration_id"])
print("Hash:", resultado["validation_hash"])
print("URL:", resultado["declaration_url"])
```

---

### Ejemplo en JavaScript / Node.js

```javascript
const API_KEY = 'tu_api_key_aqui';
const BASE_URL = 'https://declarador.usoeticoia.org';

async function crearDeclaracion(datos) {
  const response = await fetch(`${BASE_URL}/api/v1/declaracion/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(datos),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || `HTTP ${response.status}`);
  }

  return response.json();
}

// Uso
crearDeclaracion({
  language: 'es',
  ai_used: true,
  usage_types: ['writing-support'],
  ai_tool: {
    name: 'Gemini',
    version: '1.5 Pro',
    provider: 'Google',
    date_month: 2,
    date_year: 2026,
  },
  specific_purpose: 'Corrección gramatical del trabajo final',
  prompts: [{ id: '1', description: 'Corrige la gramática y el estilo del siguiente texto...' }],
  human_review: { level: 2 },
  author_name: 'Laura Fernández',
  author_email: 'laura@uni.edu',
}).then(result => {
  console.log('Declaración creada:', result.declaration_url);
});
```

---

### Ejemplo en PHP (Moodle / sistemas similares)

```php
<?php
function crear_declaracion(array $datos): array {
    $api_key = 'tu_api_key_aqui';
    $url = 'https://declarador.usoeticoia.org/api/v1/declaracion/';

    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => json_encode($datos),
        CURLOPT_HTTPHEADER     => [
            'Authorization: Bearer ' . $api_key,
            'Content-Type: application/json',
        ],
        CURLOPT_TIMEOUT        => 30,
    ]);

    $response = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($http_code !== 200) {
        throw new Exception('Error API Declarador: HTTP ' . $http_code);
    }

    return json_decode($response, true);
}

// Uso
$resultado = crear_declaracion([
    'language'         => 'es',
    'ai_used'          => true,
    'usage_types'      => ['draft'],
    'ai_tool'          => [
        'name'         => 'ChatGPT',
        'version'      => '4o',
        'provider'     => 'OpenAI',
        'date_month'   => 2,
        'date_year'    => 2026,
    ],
    'specific_purpose' => 'Redacción del TFG',
    'prompts'          => [['id' => '1', 'description' => 'Genera un borrador sobre...']],
    'human_review'     => ['level' => 3],
    'author_name'      => 'Ana Martínez',
    'author_email'     => 'ana@universidad.es',
]);

echo 'URL: ' . $resultado['declaration_url'] . PHP_EOL;
echo 'Hash: ' . $resultado['validation_hash'] . PHP_EOL;
```

---

## 7. Errores y códigos de respuesta

### `401 Unauthorized` — API key inválida

```json
{
  "success": false,
  "error": "API key inválida o inactiva"
}
```

Causas: header `Authorization` ausente, key incorrecta, o key desactivada por el administrador.

---

### `400 Bad Request` — Campos inválidos

```json
{
  "success": false,
  "errors": [
    "usage_types es requerido y no puede estar vacío",
    "ai_tool.name es requerido",
    "ai_tool.date_month debe ser un entero entre 1 y 12"
  ]
}
```

---

### `405 Method Not Allowed`

El endpoint solo acepta `POST`. No uses `GET`.

---

### `500 Internal Server Error`

Error inesperado en el servidor. Contacta al administrador si persiste.

---

## Notas adicionales

- Las declaraciones creadas vía API **siempre se guardan en la base de datos** y son accesibles en la URL devuelta.
- El `validation_hash` permite verificar la integridad de la declaración: si el contenido no fue alterado, el hash será siempre el mismo.
- No hay límite de rate por defecto, pero el administrador puede desactivar una key si detecta uso abusivo.
- Para entornos de prueba, usa datos ficticios y solicita una key de desarrollo separada.

---

*Documentación — API v1*