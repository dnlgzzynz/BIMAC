# Arquitectura del Sistema - Cubiertas Paramétricas BIMAC

## Visión General

El sistema de Cubiertas Paramétricas BIMAC está diseñado como una **plataforma modular** que permite crear múltiples proyectos de cubiertas con diferentes tipologías, compartiendo una librería core común de scripts, componentes y familias.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ARQUITECTURA DEL SISTEMA                             │
└─────────────────────────────────────────────────────────────────────────────┘

     ┌─────────────────────────────────────────────────────────────────────┐
     │                         CAPA DE PROYECTOS                           │
     │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐   │
     │  │   Museo     │  │  Estadio    │  │  Pabellón   │  │    ...    │   │
     │  │  (organic)  │  │  (tensile)  │  │ (gridshell) │  │           │   │
     │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬─────┘   │
     └─────────┼────────────────┼────────────────┼───────────────┼─────────┘
               │                │                │               │
               └────────────────┼────────────────┼───────────────┘
                                │                │
     ┌──────────────────────────┼────────────────┼─────────────────────────┐
     │                         CAPA CORE                                    │
     │  ┌───────────────────────┴────────────────┴─────────────────────┐   │
     │  │                      LIBRERÍA PYTHON                          │   │
     │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │   │
     │  │  │ geometry │  │ analysis │  │  costs   │  │   export     │   │   │
     │  │  └──────────┘  └──────────┘  └──────────┘  └──────────────┘   │   │
     │  └──────────────────────────────────────────────────────────────┘   │
     │                                                                      │
     │  ┌──────────────────────────────────────────────────────────────┐   │
     │  │                   GRASSHOPPER CLUSTERS                        │   │
     │  │  ┌───────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐   │   │
     │  │  │ Generator │ │ Analyzer │ │  Costs   │ │ RevitExporter  │   │   │
     │  │  └───────────┘ └──────────┘ └──────────┘ └────────────────┘   │   │
     │  └──────────────────────────────────────────────────────────────┘   │
     │                                                                      │
     │  ┌──────────────────────────────────────────────────────────────┐   │
     │  │                    REVIT FAMILIES                             │   │
     │  │  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐   │   │
     │  │  │ Panel_Adaptive  │  │ Node_Structural │  │ Member_Curved │   │   │
     │  │  └─────────────────┘  └─────────────────┘  └──────────────┘   │   │
     │  └──────────────────────────────────────────────────────────────┘   │
     └─────────────────────────────────────────────────────────────────────┘
                                       │
     ┌─────────────────────────────────┼───────────────────────────────────┐
     │                    CAPA DE CONFIGURACIÓN                            │
     │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
     │  │    costs.yaml    │  │  standards.yaml  │  │  materials.yaml  │   │
     │  └──────────────────┘  └──────────────────┘  └──────────────────┘   │
     └─────────────────────────────────────────────────────────────────────┘
```

---

## Capas del Sistema

### 1. Capa de Proyectos

Cada proyecto es una instancia independiente que:
- Tiene su propia configuración (`config.yaml`)
- Puede sobrescribir comportamientos del core
- Almacena sus propios exports y documentación
- Se genera desde plantillas

**Estructura de un proyecto:**
```
proyectos/museo-cubierta/
├── config.yaml          # Configuración específica
├── README.md            # Documentación del proyecto
├── src/
│   ├── grasshopper/
│   │   └── main.gh      # Definición GH (hereda de core)
│   └── overrides/       # Customizaciones
│       └── custom_geometry.py
├── docs/
│   └── notes.md
└── exports/
    ├── ifc/
    ├── excel/
    └── images/
```

### 2. Capa Core

Contiene toda la lógica reutilizable:

**Librería Python (`core/lib/`):**
```python
# Módulos disponibles
from core.lib import geometry    # Generación de superficies
from core.lib import analysis    # Análisis y validación
from core.lib import costs       # Cálculo de costos
from core.lib import export      # Exportación
from core.lib import utils       # Utilidades
```

**Grasshopper Components (`core/grasshopper/`):**
- Clusters reutilizables
- Definiciones base
- Templates de workflow

**Revit Families (`core/revit/`):**
- Familias adaptativas
- Scripts PyRevit compartidos

### 3. Capa de Configuración

Archivos YAML globales que definen:
- **costs.yaml**: Costos de materiales y factores
- **standards.yaml**: Restricciones estructurales
- **materials.yaml**: Catálogo de materiales

---

## Flujo de Datos

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FLUJO DE DATOS                                     │
└─────────────────────────────────────────────────────────────────────────────┘

     ┌──────────────┐
     │ config.yaml  │ ──────► Parámetros del proyecto
     └──────┬───────┘
            │
            ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                          GRASSHOPPER                                       │
│                                                                            │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐              │
│   │   Config     │ ──► │  Generator   │ ──► │  Panelizer   │              │
│   │   Loader     │     │  (por tipo)  │     │              │              │
│   └──────────────┘     └──────────────┘     └──────┬───────┘              │
│                                                     │                      │
│                                                     ▼                      │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐              │
│   │  Validator   │ ◄── │   Analyzer   │ ◄── │   Panels     │              │
│   │ (structural) │     │ (curvature)  │     │              │              │
│   └──────┬───────┘     └──────────────┘     └──────────────┘              │
│          │                                                                 │
│          ▼                                                                 │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐              │
│   │    Costs     │ ──► │   Reports    │ ──► │   Exporter   │              │
│   │  Calculator  │     │              │     │              │              │
│   └──────────────┘     └──────────────┘     └──────┬───────┘              │
│                                                     │                      │
└─────────────────────────────────────────────────────┼──────────────────────┘
                                                      │
            ┌─────────────────────────────────────────┼─────────────────┐
            │                                         │                 │
            ▼                                         ▼                 ▼
     ┌──────────────┐                         ┌──────────────┐  ┌──────────────┐
     │    Revit     │                         │    Excel     │  │    n8n       │
     │   (.rvt)     │                         │   Reports    │  │  Webhooks    │
     └──────────────┘                         └──────────────┘  └──────────────┘
```

---

## Patrón de Extensibilidad

### Agregar Nuevo Tipo de Cubierta

1. **Crear generador:**
```python
# core/lib/geometry/dome.py
from .base import BaseSurfaceGenerator

class DomeGenerator(BaseSurfaceGenerator):
    name = "dome"
    description = "Cúpulas geodésicas"

    def generate(self, config):
        # Implementación
        pass
```

2. **Registrar generador:**
```python
# core/lib/geometry/__init__.py
from .dome import DomeGenerator

GENERATORS = {
    ...
    "dome": DomeGenerator,
}
```

3. **Agregar configuración:**
```yaml
# config/standards.yaml
structural:
  dome:
    max_span: 40000
    min_slope: 0
    max_deflection: 300
```

4. **Agregar costos:**
```yaml
# config/costs.yaml
factors_by_type:
  dome:
    structure: 0.35
    installation: 0.18
```

### Agregar Nuevo Material

1. **Editar costs.yaml:**
```yaml
panels:
  new_material:
    flat: 800
    single_curve: 1100
    double_curve: 1600
```

2. **Agregar información:**
```yaml
materials_info:
  new_material:
    name: "Nuevo Material"
    u_value: 3.5
    weight: 8.0
```

### Sobrescribir Comportamiento por Proyecto

```python
# proyectos/mi-proyecto/src/overrides/custom_geometry.py
from core.lib.geometry.organic import OrganicGenerator

class CustomOrganicGenerator(OrganicGenerator):
    """Generador personalizado para este proyecto."""

    def generate(self, config):
        # Lógica personalizada
        surface = super().generate(config)
        # Modificaciones específicas
        return surface
```

---

## Integración con Herramientas Externas

### Grasshopper

```
┌─────────────────────────────────────────────────────────────────┐
│                      GRASSHOPPER WORKFLOW                        │
│                                                                  │
│   ┌────────────────────────────────────────────────────────┐    │
│   │  core/grasshopper/components/main_loader.gh           │    │
│   │                                                        │    │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │    │
│   │  │  Config  │  │  Core    │  │ Project  │             │    │
│   │  │  Panel   │─►│  Loader  │─►│ Selector │             │    │
│   │  └──────────┘  └──────────┘  └────┬─────┘             │    │
│   │                                   │                    │    │
│   │                                   ▼                    │    │
│   │  ┌─────────────────────────────────────────────────┐  │    │
│   │  │            WORKFLOW CLUSTERS                     │  │    │
│   │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐            │  │    │
│   │  │  │Generator│─│Panelize │─│Validate │            │  │    │
│   │  │  └─────────┘ └─────────┘ └─────────┘            │  │    │
│   │  │       │           │           │                  │  │    │
│   │  │       ▼           ▼           ▼                  │  │    │
│   │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐            │  │    │
│   │  │  │ Costs   │─│ Reports │─│ Export  │            │  │    │
│   │  │  └─────────┘ └─────────┘ └─────────┘            │  │    │
│   │  └─────────────────────────────────────────────────┘  │    │
│   └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Rhino.inside.Revit

```python
# Flujo de exportación
panels = generator.generate(config)      # Grasshopper
validated = validator.validate(panels)    # Python
costs = calculator.calculate(panels)      # Python
exporter.to_revit(panels, params)         # RiR
```

### n8n Automation

```
Webhook → Process → Airtable → Slack/Email
   │
   └── Datos: costos, paneles, estado
```

---

## Convenciones de Código

### Nomenclatura

| Tipo | Convención | Ejemplo |
|------|------------|---------|
| Clases | PascalCase | `OrganicGenerator` |
| Funciones | snake_case | `generate_surface` |
| Constantes | UPPER_SNAKE | `MAX_SPAN` |
| Archivos Python | snake_case | `organic_generator.py` |
| Archivos YAML | kebab-case | `project-config.yaml` |

### Estructura de Módulo

```python
"""
Docstring del módulo.

Descripción detallada.
"""

# Imports estándar
import os
import sys

# Imports de terceros
import yaml

# Imports locales
from .base import BaseClass

# Constantes
CONSTANT_VALUE = 42

# Clases y funciones
class MyClass:
    """Docstring de clase."""
    pass

def my_function():
    """Docstring de función."""
    pass
```

---

## Versionado

El sistema sigue **Semantic Versioning**:

```
MAJOR.MINOR.PATCH

MAJOR: Cambios incompatibles en la API
MINOR: Nueva funcionalidad compatible
PATCH: Correcciones de bugs
```

**Changelog:**

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | 2025-12-27 | Lanzamiento inicial |

---

## Referencias

- [Documentación de Rhino.inside.Revit](https://www.rhino3d.com/inside/revit/)
- [Grasshopper Developer Guide](https://developer.rhino3d.com/guides/grasshopper/)
- [Revit API Docs](https://www.revitapidocs.com/)
