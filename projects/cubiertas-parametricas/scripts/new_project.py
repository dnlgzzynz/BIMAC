#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
new_project.py - Generador de Proyectos de Cubiertas Paramétricas

Crea un nuevo proyecto a partir de la plantilla base con la estructura
y configuración necesaria.

Uso:
    python new_project.py --name "mi-proyecto" --type "organic"
    python new_project.py --name "estadio-2025" --type "tensile" --client "Municipio XYZ"
    python new_project.py --list

Opciones:
    --name      Nombre del proyecto (requerido para crear)
    --type      Tipo de cubierta (organic, tensile, gridshell, folded, shell, vault)
    --client    Nombre del cliente
    --budget    Presupuesto en MXN
    --list      Listar proyectos existentes
    --force     Sobrescribir si existe
"""

import os
import sys
import shutil
import argparse
from datetime import datetime

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# Rutas base
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates", "proyecto-base")
PROJECTS_DIR = os.path.join(PROJECT_ROOT, "proyectos")
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")

# Tipos de cubierta disponibles
SURFACE_TYPES = {
    "organic": {
        "name": "Superficie Orgánica",
        "description": "Superficies NURBS orgánicas para museos y centros culturales",
        "max_span": 15000,
        "min_slope": 2.0,
    },
    "tensile": {
        "name": "Tensoestructura",
        "description": "Membranas tensadas para estadios y grandes cubiertas",
        "max_span": 50000,
        "min_slope": 5.0,
    },
    "gridshell": {
        "name": "Gridshell",
        "description": "Mallas estructurales para pabellones e invernaderos",
        "max_span": 35000,
        "min_slope": 3.0,
    },
    "folded": {
        "name": "Placas Plegadas",
        "description": "Estructuras de placas plegadas para naves industriales",
        "max_span": 25000,
        "min_slope": 1.5,
    },
    "shell": {
        "name": "Cascarón",
        "description": "Cascarones delgados para auditorios",
        "max_span": 60000,
        "min_slope": 0,
    },
    "vault": {
        "name": "Bóveda",
        "description": "Bóvedas paramétricas para espacios culturales",
        "max_span": 30000,
        "min_slope": 0,
    },
}


def generate_project_code(name, surface_type):
    """Genera código de proyecto."""
    prefix = surface_type[:3].upper()
    date = datetime.now().strftime("%y%m")
    clean_name = "".join(c for c in name if c.isalnum())[:6].upper()
    return f"{prefix}-{clean_name}-{date}"


def create_project_config(name, surface_type, client, budget):
    """Crea el archivo de configuración del proyecto."""
    type_info = SURFACE_TYPES.get(surface_type, SURFACE_TYPES["organic"])

    config = {
        "project": {
            "name": name.replace("-", " ").title(),
            "code": generate_project_code(name, surface_type),
            "client": client or "Sin especificar",
            "created": datetime.now().strftime("%Y-%m-%d"),
            "status": "En diseño",
        },
        "geometry": {
            "type": surface_type,
            "width": 15.0,
            "length": 26.0,
            "max_height": 8.5,
            "tension": 0.65,
        },
        "constraints": {
            "max_span": type_info["max_span"] / 1000,  # Convertir a metros
            "min_slope": type_info["min_slope"],
        },
        "panels": {
            "module_width": 2.0,
            "module_height": 1.5,
            "material": "polycarbonate_16mm",
            "u_count": 13,
            "v_count": 10,
        },
        "budget": {
            "total": budget or 280000,
            "currency": "MXN",
        },
        "export": {
            "revit_family": "Cubierta_Panel_Adaptive",
            "ifc_version": "IFC4",
            "units": "millimeters",
        },
    }

    return config


def create_project_readme(name, surface_type, config):
    """Genera el README del proyecto."""
    type_info = SURFACE_TYPES.get(surface_type, SURFACE_TYPES["organic"])

    readme = f"""# {config['project']['name']}

**Código:** {config['project']['code']}
**Cliente:** {config['project']['client']}
**Tipo:** {type_info['name']}
**Fecha de Creación:** {config['project']['created']}

---

## Descripción

{type_info['description']}

---

## Parámetros del Proyecto

| Parámetro | Valor | Unidad |
|-----------|-------|--------|
| Ancho | {config['geometry']['width']} | m |
| Largo | {config['geometry']['length']} | m |
| Altura máxima | {config['geometry']['max_height']} | m |
| Luz libre máxima | {config['constraints']['max_span']} | m |
| Pendiente mínima | {config['constraints']['min_slope']} | % |
| Presupuesto | ${config['budget']['total']:,.0f} | {config['budget']['currency']} |

---

## Estructura del Proyecto

```
{name}/
├── config.yaml              # Configuración del proyecto
├── README.md                # Este archivo
├── src/
│   ├── grasshopper/
│   │   └── main.gh          # Definición principal (copiar de template)
│   └── overrides/           # Customizaciones específicas
│       └── custom_scripts/
├── docs/
│   └── notes.md
└── exports/
    ├── ifc/
    ├── excel/
    └── images/
```

---

## Inicio Rápido

1. **Cargar en Grasshopper:**
   - Abrir `core/grasshopper/components/main_loader.gh`
   - Seleccionar este proyecto en el dropdown

2. **Ajustar Parámetros:**
   - Modificar sliders según diseño
   - Verificar validaciones en tiempo real

3. **Exportar a Revit:**
   - Activar Rhino.inside.Revit
   - Ejecutar exportación desde GH

---

## Notas

_Agregar notas del proyecto aquí_

---

Generado con BIMAC Cubiertas Paramétricas v1.0
"""
    return readme


def create_directory_structure(project_path):
    """Crea la estructura de directorios del proyecto."""
    directories = [
        "src/grasshopper",
        "src/overrides/custom_scripts",
        "docs",
        "exports/ifc",
        "exports/excel",
        "exports/images",
    ]

    for dir_path in directories:
        full_path = os.path.join(project_path, dir_path)
        os.makedirs(full_path, exist_ok=True)

        # Crear .gitkeep en directorios vacíos
        gitkeep = os.path.join(full_path, ".gitkeep")
        if not os.path.exists(gitkeep):
            with open(gitkeep, 'w') as f:
                pass


def create_project(name, surface_type, client, budget, force=False):
    """
    Crea un nuevo proyecto.

    Args:
        name: Nombre del proyecto (slug)
        surface_type: Tipo de cubierta
        client: Nombre del cliente
        budget: Presupuesto
        force: Sobrescribir si existe

    Returns:
        str: Ruta del proyecto creado
    """
    # Validar tipo
    if surface_type not in SURFACE_TYPES:
        print(f"Error: Tipo '{surface_type}' no válido.")
        print(f"Tipos disponibles: {', '.join(SURFACE_TYPES.keys())}")
        return None

    # Normalizar nombre
    project_slug = name.lower().replace(" ", "-")
    project_path = os.path.join(PROJECTS_DIR, project_slug)

    # Verificar si existe
    if os.path.exists(project_path):
        if force:
            shutil.rmtree(project_path)
        else:
            print(f"Error: El proyecto '{project_slug}' ya existe.")
            print("Use --force para sobrescribir.")
            return None

    # Crear estructura
    print(f"\nCreando proyecto: {project_slug}")
    print("-" * 50)

    os.makedirs(project_path, exist_ok=True)
    create_directory_structure(project_path)
    print("  [OK] Estructura de directorios creada")

    # Crear configuración
    config = create_project_config(name, surface_type, client, budget)

    if YAML_AVAILABLE:
        config_path = os.path.join(project_path, "config.yaml")
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print("  [OK] config.yaml creado")
    else:
        # Fallback a formato simple
        config_path = os.path.join(project_path, "config.txt")
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(str(config))
        print("  [OK] config.txt creado (instalar PyYAML para formato YAML)")

    # Crear README
    readme = create_project_readme(name, surface_type, config)
    readme_path = os.path.join(project_path, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme)
    print("  [OK] README.md creado")

    # Crear notes.md
    notes_path = os.path.join(project_path, "docs", "notes.md")
    with open(notes_path, 'w', encoding='utf-8') as f:
        f.write(f"# Notas - {config['project']['name']}\n\n")
        f.write(f"**Fecha:** {config['project']['created']}\n\n")
        f.write("---\n\n")
        f.write("## Historial de cambios\n\n")
        f.write(f"- {config['project']['created']}: Proyecto creado\n\n")
    print("  [OK] docs/notes.md creado")

    print("-" * 50)
    print(f"\nProyecto creado exitosamente en:")
    print(f"  {project_path}")
    print(f"\nCódigo de proyecto: {config['project']['code']}")
    print(f"Tipo: {SURFACE_TYPES[surface_type]['name']}")

    return project_path


def list_projects():
    """Lista todos los proyectos existentes."""
    if not os.path.exists(PROJECTS_DIR):
        print("No hay proyectos creados.")
        return

    projects = []

    for name in os.listdir(PROJECTS_DIR):
        project_path = os.path.join(PROJECTS_DIR, name)
        if os.path.isdir(project_path):
            config_path = os.path.join(project_path, "config.yaml")

            info = {"name": name, "type": "-", "client": "-", "status": "-"}

            if os.path.exists(config_path) and YAML_AVAILABLE:
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                        info["type"] = config.get("geometry", {}).get("type", "-")
                        info["client"] = config.get("project", {}).get("client", "-")
                        info["status"] = config.get("project", {}).get("status", "-")
                except:
                    pass

            projects.append(info)

    if not projects:
        print("No hay proyectos creados.")
        return

    print("\nPROYECTOS EXISTENTES")
    print("=" * 70)
    print(f"{'Nombre':<25} {'Tipo':<12} {'Cliente':<20} {'Estado':<12}")
    print("-" * 70)

    for p in sorted(projects, key=lambda x: x["name"]):
        print(f"{p['name']:<25} {p['type']:<12} {p['client'][:18]:<20} {p['status']:<12}")

    print("=" * 70)
    print(f"Total: {len(projects)} proyectos")


def main():
    parser = argparse.ArgumentParser(
        description="Generador de Proyectos de Cubiertas Paramétricas BIMAC"
    )

    parser.add_argument(
        "--name",
        type=str,
        help="Nombre del proyecto"
    )

    parser.add_argument(
        "--type",
        type=str,
        default="organic",
        choices=list(SURFACE_TYPES.keys()),
        help="Tipo de cubierta"
    )

    parser.add_argument(
        "--client",
        type=str,
        default=None,
        help="Nombre del cliente"
    )

    parser.add_argument(
        "--budget",
        type=float,
        default=None,
        help="Presupuesto en MXN"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="Listar proyectos existentes"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Sobrescribir si el proyecto existe"
    )

    args = parser.parse_args()

    if args.list:
        list_projects()
        return

    if not args.name:
        print("Error: Se requiere --name para crear un proyecto.")
        print("Use --list para ver proyectos existentes.")
        print("\nEjemplo:")
        print("  python new_project.py --name 'mi-proyecto' --type 'organic'")
        return

    create_project(
        name=args.name,
        surface_type=args.type,
        client=args.client,
        budget=args.budget,
        force=args.force
    )


if __name__ == "__main__":
    main()
