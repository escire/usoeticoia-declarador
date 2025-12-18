# Guía de Versionado - Declarador.io

Este documento describe el sistema de versionado del proyecto Declarador y cómo gestionar versiones.

## Sistema de Versionado

Declarador utiliza **Semantic Versioning (SemVer)** para todas sus versiones.

### Formato de Versión

```
MAJOR.MINOR.PATCH
```

Ejemplo: `1.2.3`

- **MAJOR** (1): Cambios incompatibles con versiones anteriores
- **MINOR** (2): Nueva funcionalidad compatible con versiones anteriores
- **PATCH** (3): Correcciones de bugs compatibles

### Cuándo Incrementar Cada Número

#### MAJOR (1.0.0 → 2.0.0)
Incrementar cuando hay cambios que rompen compatibilidad:
- Cambios en la estructura de datos de declaraciones que hacen incompatibles versiones anteriores
- Cambios en API pública que requieren modificaciones de código
- Eliminación de funcionalidades existentes
- Cambios en formatos de exportación que no pueden leer versiones antiguas

Ejemplos:
- Cambio en el formato del hash de validación
- Modificación en la estructura JSON de exportación
- Eliminación de tipos de uso de IA

#### MINOR (0.1.0 → 0.2.0)
Incrementar cuando se agregan funcionalidades nuevas de forma compatible:
- Nuevas funcionalidades en el wizard
- Nuevos tipos de uso de IA
- Nuevos formatos de exportación
- Mejoras en la interfaz de usuario
- Nuevas integraciones (ej: nuevas APIs)

Ejemplos:
- Agregar un nuevo paso al wizard
- Implementar exportación a PDF
- Añadir soporte para nuevos idiomas
- Integración con servicios externos

#### PATCH (0.1.0 → 0.1.1)
Incrementar para correcciones de bugs y mejoras menores:
- Corrección de errores
- Mejoras de rendimiento
- Correcciones de seguridad
- Actualizaciones de dependencias
- Correcciones de traducciones
- Mejoras en documentación

Ejemplos:
- Corregir validación de formularios
- Arreglar estilos CSS rotos
- Actualizar traducciones incorrectas
- Mejorar mensajes de error

## Archivos del Sistema de Versionado

### VERSION
Archivo en la raíz del proyecto que contiene la versión actual:

```
0.1.0
```

Este archivo es la fuente única de verdad para la versión del proyecto.

### CHANGELOG.md
Registro cronológico de todos los cambios notables:

```markdown
## [Unreleased]
### Agregado
- Nueva funcionalidad en desarrollo

## [0.1.0] - 2025-12-18
### Agregado
- Sistema de versionado inicial
```

### Git Tags
Cada versión se etiqueta en Git con el formato `vX.Y.Z`:

```bash
git tag -l
# v0.1.0
# v0.2.0
# v1.0.0
```

## Flujo de Trabajo de Versiones

### 1. Desarrollo Normal

Durante el desarrollo, trabaja normalmente sin preocuparte por versiones:

```bash
# Haz commits normales
git add .
git commit -m "feat: nueva funcionalidad X"
git commit -m "fix: corrige bug Y"
```

Actualiza la sección `[Unreleased]` en CHANGELOG.md con tus cambios:

```markdown
## [Unreleased]
### Agregado
- Nueva funcionalidad X

### Corregido
- Bug Y en el componente Z
```

### 2. Crear una Nueva Versión

Cuando estés listo para crear un release:

#### Paso 1: Verifica la versión actual

```bash
python scripts/bump_version.py --current
# Versión actual: 0.1.0
```

#### Paso 2: Decide qué tipo de versión crear

- Bug fixes → `patch` (0.1.0 → 0.1.1)
- Nueva funcionalidad → `minor` (0.1.0 → 0.2.0)
- Cambios incompatibles → `major` (0.1.0 → 1.0.0)

#### Paso 3: Ejecuta el script de bump

```bash
# Para una corrección de bugs
python scripts/bump_version.py patch

# Para una nueva funcionalidad
python scripts/bump_version.py minor

# Para cambios incompatibles
python scripts/bump_version.py major
```

El script:
1. Actualiza el archivo VERSION
2. Convierte `[Unreleased]` en `[X.Y.Z] - FECHA` en CHANGELOG.md
3. Crea un commit automático
4. Crea un tag git (`vX.Y.Z`)

#### Paso 4: Verifica los cambios

```bash
# Ver el commit creado
git log -1

# Ver el tag creado
git tag -l | tail -1
```

#### Paso 5: Publica la versión

```bash
# Push del commit y del tag
git push origin main
git push origin v0.2.0  # Reemplaza con tu versión
```

### 3. Workflow Completo - Ejemplo

Ejemplo práctico de crear versión 0.2.0:

```bash
# 1. Verificar versión actual
python scripts/bump_version.py --current
# Versión actual: 0.1.0

# 2. Crear nueva versión minor (nueva funcionalidad)
python scripts/bump_version.py minor

# Output del script:
# === Actualizando versión ===
# Versión actual: 0.1.0
# Nueva versión:  0.2.0
#
# ¿Continuar? [y/N]: y
# ✓ Archivo VERSION actualizado a 0.2.0
# ✓ CHANGELOG.md actualizado con versión 0.2.0
# ✓ Commit creado: chore: bump version to 0.2.0
# ✓ Tag creado: v0.2.0

# 3. Revisar cambios
git log -1
git show v0.2.0

# 4. Publicar
git push origin main
git push origin v0.2.0
```

## Comandos del Script bump_version.py

### Mostrar versión actual
```bash
python scripts/bump_version.py --current
```

### Incrementar versión patch (0.1.0 → 0.1.1)
```bash
python scripts/bump_version.py patch
```

### Incrementar versión minor (0.1.0 → 0.2.0)
```bash
python scripts/bump_version.py minor
```

### Incrementar versión major (0.1.0 → 1.0.0)
```bash
python scripts/bump_version.py major
```

### Solo crear tag (sin cambiar versión)
```bash
python scripts/bump_version.py --tag
```

Útil si ya actualizaste VERSION manualmente y solo quieres el tag.

## Integración con Django

La versión está disponible en Django settings:

```python
from django.conf import settings

print(f"Versión actual: {settings.VERSION}")
```

Puedes usar esto en templates, APIs, o logging.

## Buenas Prácticas

### 1. Actualiza CHANGELOG.md constantemente
No esperes al release para documentar cambios. Actualiza `[Unreleased]` con cada feature o fix:

```markdown
## [Unreleased]
### Agregado
- Nueva funcionalidad de exportación a PDF

### Corregido
- Bug en validación de campos
```

### 2. Usa Conventional Commits
Facilita generar changelogs automáticos:

```bash
git commit -m "feat: agregar exportación a PDF"
git commit -m "fix: corregir validación de email"
git commit -m "docs: actualizar README"
git commit -m "chore: actualizar dependencias"
```

Tipos recomendados:
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Formato de código (sin cambios funcionales)
- `refactor`: Refactorización de código
- `test`: Agregar o modificar tests
- `chore`: Mantenimiento (deps, configs)

### 3. Nunca modifiques versiones publicadas
Una vez que un tag `vX.Y.Z` está en GitHub, nunca lo borres o modifiques.

Si necesitas corregir algo, crea una nueva versión patch.

### 4. Releases de GitHub
Después de crear un tag, crea un Release en GitHub:

1. Ve a `https://github.com/tu-usuario/declarador/releases/new`
2. Selecciona el tag recién creado
3. Copia los cambios del CHANGELOG.md para esa versión
4. Publica el release

## Automatización Futura

Posibles mejoras al sistema:

### GitHub Actions
Automatizar releases con CI/CD:

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags:
      - 'v*'
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          body_path: CHANGELOG.md
```

### Pre-commit Hooks
Validar que CHANGELOG.md esté actualizado antes de commits.

### Changelog Automático
Generar CHANGELOG.md automáticamente desde commits con conventional commits.

## Troubleshooting

### Error: "El tag vX.Y.Z ya existe"

El tag ya fue creado. Opciones:

```bash
# Ver tags existentes
git tag -l

# Eliminar tag local (solo si NO se ha pusheado)
git tag -d v0.2.0

# Eliminar tag remoto (¡CUIDADO!)
git push origin --delete v0.2.0
```

### Quiero cambiar versión manualmente

```bash
# 1. Edita VERSION manualmente
echo "0.3.0" > VERSION

# 2. Actualiza CHANGELOG.md manualmente
# [edita el archivo]

# 3. Commit manual
git add VERSION CHANGELOG.md
git commit -m "chore: bump version to 0.3.0"

# 4. Crea tag con el script
python scripts/bump_version.py --tag
```

### Olvidé actualizar CHANGELOG.md antes del bump

```bash
# 1. Haz reset del último commit (conserva cambios)
git reset HEAD~1

# 2. Actualiza CHANGELOG.md
# [edita el archivo]

# 3. Vuelve a ejecutar bump
python scripts/bump_version.py minor
```

## Roadmap de Versiones

Plan sugerido de versiones futuras:

- **v0.1.x**: Versiones iniciales, correcciones de bugs
- **v0.2.0**: Exportación a PDF
- **v0.3.0**: Soporte para más idiomas
- **v0.4.0**: API REST pública
- **v1.0.0**: Primera versión estable de producción
- **v1.1.0**: Integración con ORCID
- **v2.0.0**: Rediseño mayor de interfaz

## Referencias

- [Semantic Versioning](https://semver.org/lang/es/)
- [Keep a Changelog](https://keepachangelog.com/es/1.0.0/)
- [Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0/)
- [Git Tagging](https://git-scm.com/book/es/v2/Fundamentos-de-Git-Etiquetado)
