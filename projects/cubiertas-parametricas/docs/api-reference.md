# API Reference - Cubiertas Paramétricas BIMAC

Documentación de la API de la librería core para desarrollo de cubiertas paramétricas.

---

## Módulos Disponibles

```python
from core.lib import geometry    # Generación de superficies
from core.lib import analysis    # Análisis y validación
from core.lib import costs       # Cálculo de costos
from core.lib import export      # Exportación
from core.lib import utils       # Utilidades
```

---

## core.lib.geometry

### BaseSurfaceGenerator

Clase base abstracta para todos los generadores de superficies.

```python
from core.lib.geometry.base import BaseSurfaceGenerator

class CustomGenerator(BaseSurfaceGenerator):
    name = "custom"
    description = "Mi generador personalizado"

    def generate(self, config):
        # Implementación
        pass
```

**Propiedades:**
- `name` (str): Identificador único del generador
- `description` (str): Descripción del tipo de superficie
- `max_span` (float): Luz máxima por defecto (mm)
- `min_slope` (float): Pendiente mínima por defecto (%)

**Métodos:**
- `generate(config)` → `Surface`: Genera la superficie principal
- `validate_config(config)` → `bool`: Valida la configuración
- `get_default_config()` → `dict`: Retorna configuración por defecto

---

### OrganicGenerator

Generador de superficies NURBS orgánicas.

```python
from core.lib.geometry.organic import OrganicGenerator

generator = OrganicGenerator()
surface = generator.generate({
    "width": 15000,      # mm
    "length": 26000,     # mm
    "max_height": 8500,  # mm
    "tension": 0.65,     # 0-1
    "asymmetry": 0.0     # -1 a 1
})
```

**Parámetros de Configuración:**

| Parámetro | Tipo | Descripción | Rango |
|-----------|------|-------------|-------|
| `width` | float | Ancho de la superficie | > 0 |
| `length` | float | Largo de la superficie | > 0 |
| `max_height` | float | Altura máxima en cenit | > 0 |
| `tension` | float | Factor de curvatura | 0.0 - 1.0 |
| `asymmetry` | float | Factor de asimetría | -1.0 - 1.0 |
| `curve_degree` | int | Grado de curvas | 2, 3, o 5 |
| `rebuild_count` | int | Puntos de reconstrucción | > 10 |

---

### TensileGenerator

Generador de superficies de tensoestructura.

```python
from core.lib.geometry.tensile import TensileGenerator

generator = TensileGenerator()
surface = generator.generate({
    "width": 45000,
    "length": 60000,
    "peak_heights": [18000, 16000],
    "pretension": 0.8,
    "membrane_type": "anticlastic"
})
```

**Parámetros de Configuración:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `width` | float | Ancho de la membrana |
| `length` | float | Largo de la membrana |
| `peak_heights` | list[float] | Alturas de los puntos altos |
| `pretension` | float | Factor de pretensión (0-1) |
| `membrane_type` | str | `anticlastic` o `synclastic` |
| `anchor_points` | list[Point3d] | Puntos de anclaje |

---

### Panelizer

Divide una superficie en paneles optimizados.

```python
from core.lib.geometry.panelizer import Panelizer

panelizer = Panelizer()
result = panelizer.panelize(
    surface=my_surface,
    u_count=13,
    v_count=10,
    tolerance=5.0
)

# Acceder a resultados
flat_panels = result.flat
single_curve = result.single_curve
double_curve = result.double_curve
statistics = result.stats
```

**Métodos:**

#### `panelize(surface, u_count, v_count, tolerance=5.0)`

Divide la superficie en paneles y los clasifica.

**Parámetros:**
- `surface` (Surface): Superficie a panelizar
- `u_count` (int): Divisiones en dirección U
- `v_count` (int): Divisiones en dirección V
- `tolerance` (float): Tolerancia de planarización (mm)

**Retorna:** `PanelizationResult`
- `.flat` (list[Brep]): Paneles planos
- `.single_curve` (list[Brep]): Paneles de curvatura simple
- `.double_curve` (list[Brep]): Paneles de doble curvatura
- `.stats` (dict): Estadísticas de la panelización

---

#### `rationalize(panels, method="planar", tolerance=5.0)`

Racionaliza paneles para fabricación.

**Parámetros:**
- `panels` (list[Brep]): Lista de paneles
- `method` (str): `planar`, `cylindrical`, o `conical`
- `tolerance` (float): Tolerancia de racionalización

**Retorna:** `list[Brep]` - Paneles racionalizados

---

## core.lib.analysis

### CurvatureAnalyzer

Analiza la curvatura de superficies y paneles.

```python
from core.lib.analysis.curvature import CurvatureAnalyzer

analyzer = CurvatureAnalyzer()
result = analyzer.analyze_surface(surface, resolution=20)

# Acceder a resultados
gaussian = result.gaussian_curvature  # Matriz de valores K
mean = result.mean_curvature          # Matriz de valores H
max_k = result.max_gaussian
min_k = result.min_gaussian
```

**Métodos:**

#### `analyze_surface(surface, resolution=20)`

Analiza la curvatura en una grilla de puntos.

**Parámetros:**
- `surface` (Surface): Superficie a analizar
- `resolution` (int): Resolución de la grilla (NxN)

**Retorna:** `CurvatureResult`
- `.gaussian_curvature` (2D array): Valores de curvatura Gaussiana
- `.mean_curvature` (2D array): Valores de curvatura media
- `.principal_curvatures` (tuple): (k1, k2) matrices
- `.max_gaussian` (float): Máximo valor de K
- `.min_gaussian` (float): Mínimo valor de K
- `.points` (list[Point3d]): Puntos de análisis

---

#### `classify_panel(panel, tolerance=5.0)`

Clasifica un panel por su curvatura.

**Parámetros:**
- `panel` (Brep): Panel a clasificar
- `tolerance` (float): Tolerancia de planaridad (mm)

**Retorna:** `str` - `"flat"`, `"single_curve"`, o `"double_curve"`

---

### StructuralValidator

Valida restricciones estructurales de la cubierta.

```python
from core.lib.analysis.structural import StructuralValidator

validator = StructuralValidator(
    max_span=15000,
    min_slope=2.0,
    max_deflection=104
)

result = validator.validate(surface)

if result.is_valid:
    print("Superficie válida")
else:
    for warning in result.warnings:
        print(f"Advertencia: {warning}")
```

**Constructor:**

```python
StructuralValidator(
    max_span=15000,       # mm
    min_slope=2.0,        # %
    max_deflection=None   # mm (opcional)
)
```

**Métodos:**

#### `validate(surface)`

Ejecuta todas las validaciones.

**Retorna:** `ValidationResult`
- `.is_valid` (bool): Si pasó todas las validaciones
- `.results` (list[CheckResult]): Resultados individuales
- `.warnings` (list[str]): Advertencias
- `.critical_points` (list[Point3d]): Puntos problemáticos

---

#### `check_max_span(surface)`

Verifica la luz libre máxima.

**Retorna:** `CheckResult`

---

#### `check_min_slope(surface)`

Verifica la pendiente mínima para drenaje.

**Retorna:** `CheckResult`

---

## core.lib.costs

### CostCalculator

Calcula costos del proyecto.

```python
from core.lib.costs.calculator import CostCalculator

calculator = CostCalculator(material="polycarbonate_16mm")

project_cost, breakdowns = calculator.calculate(
    flat_panels=flat_list,
    single_curve=single_list,
    double_curve=double_list,
    budget=280000
)

# Acceder a resultados
print(f"Total: ${project_cost.total:,.2f}")
print(f"Dentro de presupuesto: {project_cost.is_within_budget}")

# Generar reporte
report = calculator.generate_report(project_cost, breakdowns)
print(report)
```

**Constructor:**

```python
CostCalculator(
    material="polycarbonate_16mm",  # Material base
    costs=None,                      # Dict de costos personalizados
    factors=None,                    # Factores adicionales
    discounts=None,                  # Descuentos por volumen
    config_path=None                 # Ruta a archivo YAML
)
```

**Materiales Disponibles:**
- `polycarbonate_16mm`
- `polycarbonate_10mm`
- `glass_laminated`
- `etfe_single`
- `metal_composite`

---

#### `calculate(...)`

Calcula el costo total del proyecto.

**Parámetros:**
- `flat_panels` (list[Brep]): Paneles planos
- `single_curve` (list[Brep]): Paneles curvatura simple
- `double_curve` (list[Brep]): Paneles doble curvatura
- `flat_area` (float): Alternativa: área de paneles planos (m²)
- `single_area` (float): Alternativa: área curvatura simple
- `double_area` (float): Alternativa: área doble curvatura
- `budget` (float): Presupuesto disponible

**Retorna:** `tuple(ProjectCost, dict[CostBreakdown])`

---

### ProjectCost (NamedTuple)

```python
ProjectCost(
    panels_cost=150000,        # Costo de paneles
    structure_cost=37500,      # Costo de estructura
    installation_cost=28125,   # Costo de instalación
    contingency=21562,         # Contingencia
    total=237187,              # Total
    budget=280000,             # Presupuesto
    margin=42813,              # Margen
    margin_percent=15.3,       # Porcentaje de margen
    is_within_budget=True      # Si está dentro
)
```

---

### CostBreakdown (NamedTuple)

```python
CostBreakdown(
    panel_type="flat",
    material="polycarbonate_16mm",
    quantity=80,
    area=240.5,
    cost_per_m2=450,
    subtotal=108225
)
```

---

### Función de Conveniencia

```python
from core.lib.costs import calculate_costs

project_cost, breakdowns = calculate_costs(
    flat_area=200,
    single_area=80,
    double_area=20,
    material="glass_laminated",
    budget=500000
)
```

---

## core.lib.export

### RevitExporter

Exporta paneles a Revit usando Rhino.inside.Revit.

```python
from core.lib.export.revit import RevitExporter

exporter = RevitExporter(
    family_name="Cubierta_Panel_Adaptive",
    category="Roofs"
)

# Exportar paneles
result = exporter.export_panels(
    panels=all_panels,
    curvature_data=curvature_list,
    cost_data=cost_list
)

# Crear schedule
exporter.create_schedule("BIMAC_Cubierta_Paneles")
```

---

### IFCExporter

Exporta a formato IFC.

```python
from core.lib.export.ifc import IFCExporter

exporter = IFCExporter(version="IFC4")

exporter.export(
    panels=all_panels,
    output_path="exports/ifc/cubierta.ifc",
    metadata={
        "project_name": "Museo Cubierta",
        "author": "BIMAC"
    }
)
```

---

### ExcelExporter

Genera reportes en Excel.

```python
from core.lib.export.excel import ExcelExporter

exporter = ExcelExporter()

exporter.generate_report(
    project_cost=cost_result,
    breakdowns=breakdowns,
    panels_data=panels_info,
    output_path="exports/excel/reporte.xlsx"
)
```

---

## core.lib.utils

### ConfigLoader

Carga y valida archivos de configuración YAML.

```python
from core.lib.utils.config import ConfigLoader

loader = ConfigLoader()

# Cargar configuración de proyecto
config = loader.load("proyectos/mi-museo/config.yaml")

# Acceder a valores
width = config.get("geometry", {}).get("width", 15.0)

# Validar configuración
is_valid, errors = loader.validate(config, schema="project")
```

---

### Units

Utilidades de conversión de unidades.

```python
from core.lib.utils.units import Units

# Conversiones
mm = Units.m_to_mm(15.0)      # 15000.0
m = Units.mm_to_m(26000)      # 26.0

# Formato
formatted = Units.format_currency(280000, "MXN")  # "$280,000.00 MXN"
area_str = Units.format_area(390.5)               # "390.50 m²"
```

---

### Logger

Sistema de logging para scripts.

```python
from core.lib.utils.logger import Logger

log = Logger("my_module")

log.info("Proceso iniciado")
log.warning("Luz libre cercana al límite")
log.error("No se pudo cargar configuración")
log.debug("Valor de tensión: 0.65")
```

---

## Tipos y Constantes

### Surface Types

```python
from core.lib import SURFACE_TYPES

# Disponibles:
# "organic", "tensile", "gridshell", "folded", "shell", "vault"
```

### Panel Types

```python
from core.lib import PANEL_TYPES

# "flat", "single_curve", "double_curve"
```

### Materials

```python
from core.lib import MATERIALS

# "polycarbonate_16mm", "polycarbonate_10mm",
# "glass_laminated", "etfe_single", "metal_composite"
```

---

## Ejemplos de Uso

### Flujo Completo

```python
from core.lib.geometry.organic import OrganicGenerator
from core.lib.geometry.panelizer import Panelizer
from core.lib.analysis.curvature import CurvatureAnalyzer
from core.lib.analysis.structural import StructuralValidator
from core.lib.costs.calculator import CostCalculator

# 1. Generar superficie
generator = OrganicGenerator()
surface = generator.generate({
    "width": 15000,
    "length": 26000,
    "max_height": 8500,
    "tension": 0.65
})

# 2. Validar estructura
validator = StructuralValidator(max_span=15000, min_slope=2.0)
validation = validator.validate(surface)

if not validation.is_valid:
    print("Errores de validación:")
    for warning in validation.warnings:
        print(f"  - {warning}")

# 3. Panelizar
panelizer = Panelizer()
panels = panelizer.panelize(surface, u_count=13, v_count=10)

print(f"Paneles planos: {len(panels.flat)}")
print(f"Curvatura simple: {len(panels.single_curve)}")
print(f"Doble curvatura: {len(panels.double_curve)}")

# 4. Calcular costos
calculator = CostCalculator(material="polycarbonate_16mm")
cost, breakdowns = calculator.calculate(
    flat_panels=panels.flat,
    single_curve=panels.single_curve,
    double_curve=panels.double_curve,
    budget=280000
)

# 5. Generar reporte
report = calculator.generate_report(cost, breakdowns)
print(report)
```

---

## Extensibilidad

### Crear Nuevo Generador

```python
from core.lib.geometry.base import BaseSurfaceGenerator

class MyCustomGenerator(BaseSurfaceGenerator):
    name = "custom"
    description = "Mi generador personalizado"
    max_span = 20000
    min_slope = 3.0

    def generate(self, config):
        import Rhino.Geometry as rg

        # Tu lógica de generación
        surface = rg.NurbsSurface.Create(...)

        return surface

    def validate_config(self, config):
        required = ["width", "length"]
        return all(k in config for k in required)
```

### Registrar en el Sistema

```python
# core/lib/geometry/__init__.py
from .my_custom import MyCustomGenerator

GENERATORS["custom"] = MyCustomGenerator
```

---

## Manejo de Errores

```python
from core.lib.exceptions import (
    ConfigurationError,
    ValidationError,
    GeometryError,
    ExportError
)

try:
    surface = generator.generate(config)
except ConfigurationError as e:
    print(f"Error de configuración: {e}")
except GeometryError as e:
    print(f"Error de geometría: {e}")
```

---

## Referencias

- [Rhino.Geometry API](https://developer.rhino3d.com/api/RhinoCommon/html/N_Rhino_Geometry.htm)
- [Revit API Docs](https://www.revitapidocs.com/)
- [IFC Schema](https://standards.buildingsmart.org/IFC/DEV/IFC4_2/FINAL/HTML/)

---

*API Reference v1.0 - BIMAC Cubiertas Paramétricas*
