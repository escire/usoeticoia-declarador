#!/usr/bin/env python3
"""
Script para gestionar versiones del proyecto Declarador.
Usa Semantic Versioning (MAJOR.MINOR.PATCH)

Uso:
    python scripts/bump_version.py patch  # 0.1.0 -> 0.1.1
    python scripts/bump_version.py minor  # 0.1.0 -> 0.2.0
    python scripts/bump_version.py major  # 0.1.0 -> 1.0.0
    python scripts/bump_version.py --current  # Muestra versión actual
    python scripts/bump_version.py --tag  # Crea git tag sin cambiar versión
"""

import sys
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

# Configuración de rutas
PROJECT_ROOT = Path(__file__).parent.parent
VERSION_FILE = PROJECT_ROOT / 'VERSION'
CHANGELOG_FILE = PROJECT_ROOT / 'CHANGELOG.md'


def get_current_version():
    """Lee la versión actual del archivo VERSION"""
    if not VERSION_FILE.exists():
        print("Error: Archivo VERSION no encontrado")
        sys.exit(1)

    version = VERSION_FILE.read_text().strip()
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        print(f"Error: Formato de versión inválido: {version}")
        sys.exit(1)

    return version


def parse_version(version):
    """Convierte string de versión a tupla (major, minor, patch)"""
    parts = version.split('.')
    return tuple(map(int, parts))


def bump_version(current_version, bump_type):
    """Incrementa la versión según el tipo de bump"""
    major, minor, patch = parse_version(current_version)

    if bump_type == 'major':
        return f"{major + 1}.0.0"
    elif bump_type == 'minor':
        return f"{major}.{minor + 1}.0"
    elif bump_type == 'patch':
        return f"{major}.{minor}.{patch + 1}"
    else:
        print(f"Error: Tipo de bump inválido: {bump_type}")
        print("Usa: major, minor, o patch")
        sys.exit(1)


def update_version_file(new_version):
    """Actualiza el archivo VERSION"""
    VERSION_FILE.write_text(f"{new_version}\n")
    print(f"✓ Archivo VERSION actualizado a {new_version}")


def update_changelog(new_version):
    """Actualiza CHANGELOG.md con la nueva versión"""
    if not CHANGELOG_FILE.exists():
        print("WARNING: Archivo CHANGELOG.md no encontrado, saltando actualización")
        return

    content = CHANGELOG_FILE.read_text()
    today = datetime.now().strftime('%Y-%m-%d')

    # Buscar sección [Unreleased] y reemplazarla
    unreleased_pattern = r'## \[Unreleased\]'
    new_section = f"## [Unreleased]\n\n## [{new_version}] - {today}"

    if re.search(unreleased_pattern, content):
        updated_content = re.sub(unreleased_pattern, new_section, content, count=1)
        CHANGELOG_FILE.write_text(updated_content)
        print(f"✓ CHANGELOG.md actualizado con versión {new_version}")
    else:
        print("WARNING: No se encontró sección [Unreleased] en CHANGELOG.md")
        print("  Puedes actualizarlo manualmente")


def git_commit_version(version):
    """Crea commit con los cambios de versión"""
    try:
        # Verificar si hay cambios
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )

        if not result.stdout.strip():
            print("WARNING: No hay cambios para commitear")
            return False

        # Añadir archivos modificados
        subprocess.run(['git', 'add', 'VERSION', 'CHANGELOG.md'], cwd=PROJECT_ROOT, check=True)

        # Crear commit
        commit_message = f"chore: bump version to {version}"
        subprocess.run(
            ['git', 'commit', '-m', commit_message],
            cwd=PROJECT_ROOT,
            check=True
        )

        print(f"✓ Commit creado: {commit_message}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"WARNING: Error al crear commit: {e}")
        return False


def git_create_tag(version):
    """Crea un git tag para la versión"""
    try:
        tag_name = f"v{version}"
        tag_message = f"Release version {version}"

        # Verificar si el tag ya existe
        result = subprocess.run(
            ['git', 'tag', '-l', tag_name],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )

        if result.stdout.strip():
            print(f"WARNING: El tag {tag_name} ya existe")
            return False

        # Crear tag anotado
        subprocess.run(
            ['git', 'tag', '-a', tag_name, '-m', tag_message],
            cwd=PROJECT_ROOT,
            check=True
        )

        print(f"✓ Tag creado: {tag_name}")
        print(f"\nPara publicar el tag ejecuta:")
        print(f"  git push origin {tag_name}")
        print(f"  git push origin main")
        return True

    except subprocess.CalledProcessError as e:
        print(f"WARNING: Error al crear tag: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Uso: python scripts/bump_version.py [major|minor|patch|--current|--tag]")
        print("\nEjemplos:")
        print("  python scripts/bump_version.py patch   # Incrementa versión patch")
        print("  python scripts/bump_version.py minor   # Incrementa versión minor")
        print("  python scripts/bump_version.py major   # Incrementa versión major")
        print("  python scripts/bump_version.py --current  # Muestra versión actual")
        print("  python scripts/bump_version.py --tag   # Solo crea git tag")
        sys.exit(1)

    command = sys.argv[1]
    current_version = get_current_version()

    # Mostrar versión actual
    if command == '--current':
        print(f"Versión actual: {current_version}")
        sys.exit(0)

    # Solo crear tag
    if command == '--tag':
        print(f"Creando tag para versión actual: {current_version}")
        git_create_tag(current_version)
        sys.exit(0)

    # Incrementar versión
    if command not in ['major', 'minor', 'patch']:
        print(f"Error: Comando desconocido '{command}'")
        print("Usa: major, minor, patch, --current, o --tag")
        sys.exit(1)

    new_version = bump_version(current_version, command)

    print(f"\n=== Actualizando versión ===")
    print(f"Versión actual: {current_version}")
    print(f"Nueva versión:  {new_version}")
    print()

    # Confirmar cambio
    response = input("¿Continuar? [y/N]: ").strip().lower()
    if response not in ['y', 'yes', 's', 'si', 'sí']:
        print("Operación cancelada")
        sys.exit(0)

    # Actualizar archivos
    update_version_file(new_version)
    update_changelog(new_version)

    # Git operations
    print("\n=== Operaciones Git ===")
    commit_created = git_commit_version(new_version)

    if commit_created:
        tag_created = git_create_tag(new_version)

        if tag_created:
            print("\n✓ ¡Versión actualizada exitosamente!")
            print(f"\nPróximos pasos:")
            print(f"  1. Revisa los cambios: git log -1")
            print(f"  2. Push del commit: git push origin main")
            print(f"  3. Push del tag: git push origin v{new_version}")
    else:
        print("\n✓ Archivos actualizados (sin commit automático)")
        print("Puedes hacer commit manualmente con:")
        print(f"  git add VERSION CHANGELOG.md")
        print(f"  git commit -m 'chore: bump version to {new_version}'")
        print(f"  git tag -a v{new_version} -m 'Release version {new_version}'")


if __name__ == '__main__':
    main()
