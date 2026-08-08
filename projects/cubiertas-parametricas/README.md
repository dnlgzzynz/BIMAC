# Cubiertas Paramétricas - Sistema de Plantillas BIMAC

Sistema modular para diseño y fabricación de cubiertas paramétricas con integración Grasshopper + Revit.

---

## Arquitectura del Sistema

```
cubiertas-parametricas/
│
├── core/                        # LIBRERÍA COMPARTIDA (no modificar por proyecto)
│   ├── lib/                     # Scripts Python reutilizables
│   │   ├── geometry/            # Funciones de geometría
│   │   ├── analysis/            # Análisis estructural y curvatura
│   │   ├── costs/               # Cálculo de costos
│   │   ├── export/              # Exportación (Revit, IFC, Excel)
│   │   └── utils/               # Utilidades generales
│   ├── grasshopper/
│   │   ├── components/          # Definiciones GH base (.gh)
│   │   └── clusters/            # Clusters reutilizables (.ghcluster)
│   ├── revit/
│   │   ├── families/            # Familias adaptativas base (.rfa)
│   │   └── scripts/             # Scripts PyRevit compartidos
│   └── n8n/                     # Workflows de automatización
│
├── templates/                   # PLANTILLAS DE PROYECTO
│   └── proyecto-base/           # Template para nuevos proyectos
│       ├── config.yaml          # Configuración del proyecto
│       ├── src/                 # Código específico del proyecto
│       ├── docs/                # Documentación
│       └── exports/             # Salidas
│
├── proyectos/                   # PROYECTOS GENERADOS
│   ├── museo-cubierta-organica/
│   ├── estadio-tensoestructura/
│   ├── pabellon-expo-2025/
│   └── ...
│
├── config/                      # CONFIGURACIÓN GLOBAL
│   ├── costs.yaml               # Costos de materiales
│   ├── materials.yaml           # Catálogo de materiales
│   ├── standards.yaml           # Estándares estructurales
│   └── export_settings.yaml     # Configuración de exportación
│
├── scripts/                     # SCRIPTS DE GESTIÓN
│   ├── new_project.py           # Generador de proyectos
│   ├── sync_core.py             # Sincronizar core a proyectos
│   └── build_release.py         # Empaquetar para distribución
│
└── docs/                        # DOCUMENTACIÓN GENERAL
    ├── architecture.md          # Arquitectura del sistema
    ├── getting-started.md       # Guía de inicio
    ├── api-reference.md         # Referencia de API
    └── tutorials/               # Tutoriales
```

---

## Inicio Rápido

### 1. Crear Nuevo Proyecto

```bash
python scripts/new_project.py --name "estadio-tensoestructura" --type "tensile"
```

Esto genera:
```
proyectos/estadio-tensoestructura/
├── config.yaml              # Configuración específica
├── src/
│   ├── grasshopper/
│   │   └── main.gh          # Definición principal (heredada de core)
│   └── overrides/           # Customizaciones del proyecto
├── docs/
└── exports/
```

### 2. Configurar Proyecto

Editar `proyectos/estadio-tensoestructura/config.yaml`:

```yaml
project:
  name: "Estadio Municipal - Tensoestructura"
  code: "EST-TENSO-001"
  client: "Municipio XYZ"

geometry:
  type: "tensile"              # organic | tensile | gridshell | folded
  width: 45.0                  # metros
  length: 60.0
  max_height: 18.0

constraints:
  max_span: 30.0               # luz libre máxima
  min_slope: 3.0               # pendiente mínima %

panels:
  module_width: 2.5
  module_height: 2.0

budget:
  total: 1500000               # MXN
  currency: "MXN"
```

### 3. Ejecutar en Grasshopper

1. Abrir `core/grasshopper/components/main_loader.gh`
2. Seleccionar proyecto en el dropdown
3. Ajustar parámetros con sliders
4. Ver resultados en tiempo real

---

## Tipos de Cubierta Soportados

| Tipo | Descripción | Complejidad | Uso Típico |
|------|-------------|-------------|------------|
| `organic` | Superficies NURBS orgánicas | Media | Museos, centros culturales |
| `tensile` | Membranas tensadas | Alta | Estadios, plazas |
| `gridshell` | Mallas estructurales | Alta | Pabellones, invernaderos |
| `folded` | Placas plegadas | Baja | Naves industriales |
| `shell` | Cascarones delgados | Media | Auditorios |
| `vault` | Bóvedas paramétricas | Media | Espacios religiosos |

---

## Flujo de Trabajo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FLUJO DE TRABAJO                                   │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │  new_project │ ─────► Genera estructura desde template
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ config.yaml  │ ─────► Define parámetros del proyecto
    └──────┬───────┘
           │
           ▼
┌──────────────────────┐
│    GRASSHOPPER       │
│  ┌────────────────┐  │
│  │  core/loader   │  │ ◄─── Carga librerías compartidas
│  └───────┬────────┘  │
│          │           │
│  ┌───────▼────────┐  │
│  │ proyecto/main  │  │ ◄─── Usa configuración del proyecto
│  └───────┬────────┘  │
│          │           │
│  ┌───────▼────────┐  │
│  │   overrides    │  │ ◄─── Aplica customizaciones
│  └────────────────┘  │
└──────────┬───────────┘
           │
           ▼
    ┌──────────────┐
    │  Validación  │ ─────► Verifica restricciones
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   Costos     │ ─────► Calcula presupuesto
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │    Revit     │ ─────► Exporta modelo BIM
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  Reportes    │ ─────► Excel, PDF, n8n
    └──────────────┘
```

---

## Librería Core

### Módulos Python

| Módulo | Funciones Principales |
|--------|----------------------|
| `core.lib.geometry` | Superficies, curvas, panelización |
| `core.lib.analysis` | Curvatura, validación estructural |
| `core.lib.costs` | Cálculo de costos, presupuestos |
| `core.lib.export` | Revit, IFC, Excel, JSON |
| `core.lib.utils` | Conversiones, logging, config |

### Clusters de Grasshopper

| Cluster | Descripción |
|---------|-------------|
| `SurfaceGenerator.ghcluster` | Genera superficies por tipo |
| `PanelOptimizer.ghcluster` | Panelización y racionalización |
| `CurvatureAnalyzer.ghcluster` | Análisis de curvatura |
| `CostCalculator.ghcluster` | Cálculo de costos en tiempo real |
| `RevitExporter.ghcluster` | Exportación a Revit |
| `StructuralValidator.ghcluster` | Validación de restricciones |

### Familias de Revit

| Familia | Uso |
|---------|-----|
| `Panel_Adaptive_4pt.rfa` | Panel cuadrilátero adaptativo |
| `Panel_Adaptive_3pt.rfa` | Panel triangular adaptativo |
| `Node_Structural.rfa` | Nodo de conexión estructural |
| `Member_Curved.rfa` | Elemento estructural curvo |

---

## Configuración Global

### costs.yaml

```yaml
# Costos por tipo de panel (MXN/m²)
panels:
  flat:
    polycarbonate_16mm: 450
    glass_laminated: 1200
    etfe_single: 800
  single_curve:
    polycarbonate_16mm: 680
    glass_curved: 1800
    etfe_cushion: 1100
  double_curve:
    polycarbonate_10mm: 1250
    glass_cold_bent: 2500
    etfe_complex: 1500

# Factores adicionales
factors:
  structure: 0.25        # 25% del costo de paneles
  installation: 0.15     # 15% del subtotal
  contingency: 0.10      # 10% de imprevistos

# Descuentos por volumen
volume_discounts:
  - min_area: 500
    discount: 0.05
  - min_area: 1000
    discount: 0.10
  - min_area: 2000
    discount: 0.15
```

### standards.yaml

```yaml
# Restricciones estructurales por tipo
structural:
  organic:
    max_span: 15000      # mm
    min_slope: 2.0       # %
    max_deflection: "L/250"
  tensile:
    max_span: 30000
    min_slope: 5.0
    max_deflection: "L/50"
  gridshell:
    max_span: 25000
    min_slope: 3.0
    max_deflection: "L/200"

# Tolerancias de fabricación
fabrication:
  panel_length: 2        # mm
  panel_width: 2
  planarity: 5
  curvature_radius: 50
```

---

## Comandos de Gestión

```bash
# Crear nuevo proyecto
python scripts/new_project.py --name "mi-proyecto" --type "organic"

# Listar proyectos existentes
python scripts/new_project.py --list

# Sincronizar core a un proyecto
python scripts/sync_core.py --project "mi-proyecto"

# Sincronizar core a todos los proyectos
python scripts/sync_core.py --all

# Validar configuración de proyecto
python scripts/validate_project.py --project "mi-proyecto"

# Generar reporte de todos los proyectos
python scripts/report.py --all --format excel

# Empaquetar proyecto para entrega
python scripts/build_release.py --project "mi-proyecto" --version "1.0.0"
```

---

## Extensibilidad

### Agregar Nuevo Tipo de Cubierta

1. Crear generador en `core/lib/geometry/`:
```python
# core/lib/geometry/dome_generator.py
class DomeGenerator(BaseSurfaceGenerator):
    def generate(self, config):
        # Implementación
        pass
```

2. Registrar en `core/lib/geometry/__init__.py`:
```python
SURFACE_GENERATORS = {
    "organic": OrganicGenerator,
    "tensile": TensileGenerator,
    "dome": DomeGenerator,  # Nuevo
}
```

3. Agregar configuración en `config/standards.yaml`:
```yaml
structural:
  dome:
    max_span: 40000
    min_slope: 0
    max_deflection: "L/300"
```

### Agregar Nuevo Material

1. Editar `config/materials.yaml`
2. Agregar costos en `config/costs.yaml`
3. Crear familia de Revit si es necesario

---

## Proyectos de Ejemplo

### 1. Museo - Cubierta Orgánica
- **Tipo:** organic
- **Área:** ~400 m²
- **Luz libre:** 15 m
- **Presupuesto:** $280,000 MXN

### 2. Estadio - Tensoestructura
- **Tipo:** tensile
- **Área:** ~2,700 m²
- **Luz libre:** 45 m
- **Presupuesto:** $1,500,000 MXN

### 3. Pabellón Expo - Gridshell
- **Tipo:** gridshell
- **Área:** ~800 m²
- **Luz libre:** 25 m
- **Presupuesto:** $650,000 MXN

---

## Requisitos

### Software
- Rhino 7/8 + Grasshopper
- Revit 2024+
- Rhino.inside.Revit
- Python 3.9+
- Node.js 18+ (para n8n)

### Plugins de Grasshopper
- Lunchbox
- Pufferfish
- Weaverbird
- Kangaroo 2 (para tensile)
- Karamba3D (opcional, para análisis)

---

## Licencia

Uso interno BIMAC. Todos los derechos reservados.

---

## Contacto

**BIMAC - BIM Advance Consulting**
- Web: [bimac.io](https://www.bimac.io)
- Email: dev@bimac.io
